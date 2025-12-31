from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import render,redirect
from django.http import HttpResponseBadRequest
from django.db.models import Q
from django.db import transaction

from accounts.decorators import role_required
from .models import Stock, StockTxn, Item
from .forms import ItemForm
from .forms import StockTxnForm
from django.db.models import F
from django.db.models import Case, When, Value, BooleanField
from django.db.models.functions import Greatest

@method_decorator(login_required, name="dispatch")
class ItemListView(ListView):
    model = Item
    template_name = "inventory/item_list.html"
    context_object_name = "items"
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(
                Q(code__icontains=q) |
                Q(name__icontains=q) |
                Q(spec__icontains=q) |
                Q(category__icontains=q) |
                Q(location__icontains=q)
            )
        return qs

@method_decorator(login_required, name="dispatch")
class ItemDetailView(DetailView):
    model = Item
    template_name = "inventory/item_detail.html"
    context_object_name = "item"

@method_decorator([login_required, role_required("keeper")], name="dispatch")
class ItemCreateView(CreateView):
    model = Item
    form_class = ItemForm
    template_name = "inventory/item_form.html"
    success_url = reverse_lazy("item_list")

@method_decorator([login_required, role_required("keeper")], name="dispatch")
class ItemUpdateView(UpdateView):
    model = Item
    form_class = ItemForm
    template_name = "inventory/item_form.html"
    success_url = reverse_lazy("item_list")

@method_decorator([login_required, role_required("keeper")], name="dispatch")
class ItemDeleteView(DeleteView):
    model = Item
    template_name = "inventory/item_confirm_delete.html"
    success_url = reverse_lazy("item_list")


from django.db.models import F, Q, Case, When, Value, BooleanField

@login_required
def stock_list(request):
    q = request.GET.get("q", "").strip()

    rows = (
        Stock.objects.select_related("item")
        .annotate(
            is_low=Case(
                When(qty__lt=F("item__min_stock"), then=Value(True)),
                default=Value(False),
                output_field=BooleanField(),
            )
        )
        # --- 新增这行代码 ---
        # 直接在数据库层面计算：建议补货量 = 最低库存 - 当前库存
        .annotate(restock_need=Greatest(F("item__min_stock") - F("qty"), Value(0)))
        .order_by("item__code")
    )

    if q:
        rows = rows.filter(
            Q(item__code__icontains=q) |
            Q(item__name__icontains=q) |
            Q(item__spec__icontains=q) |
            Q(item__category__icontains=q) |
            Q(item__location__icontains=q)
        )

    low_count = rows.filter(is_low=True).count()

    return render(
        request,
        "inventory/stock_list.html",
        {"rows": rows, "q": q, "low_count": low_count},
    )


def low_stock_list(request):
    q = request.GET.get("q", "").strip()

    rows = (
        Stock.objects.select_related("item")
        .filter(qty__lt=F("item__min_stock"))
        .annotate(restock_need=Greatest(F("item__min_stock") - F("qty"), Value(0)))
        .order_by("item__code")
    )

    if q:
        rows = rows.filter(
            Q(item__code__icontains=q) |
            Q(item__name__icontains=q) |
            Q(item__spec__icontains=q) |
            Q(item__category__icontains=q) |
            Q(item__location__icontains=q)
        )

    return render(request, "inventory/low_stock_list.html", {"rows": rows, "q": q})


@login_required
def txn_list(request):
    # 所有人可看
    txns = StockTxn.objects.select_related("item", "created_by").all()[:200]
    return render(request, "inventory/txn_list.html", {"txns": txns})


@transaction.atomic
def _apply_txn(*, user, txn_type: str, item: Item, qty: int, note: str):
    # 锁库存行，避免并发下出错
    stock, _ = Stock.objects.select_for_update().get_or_create(item=item, defaults={"qty": 0})

    if txn_type == StockTxn.IN:
        stock.qty += qty
    elif txn_type == StockTxn.OUT:
        if stock.qty < qty:
            raise ValueError(f"库存不足：当前 {stock.qty}，需要 {qty}")
        stock.qty -= qty
    else:
        raise ValueError("未知的 txn_type")

    stock.save()

    StockTxn.objects.create(
        item=item,
        txn_type=txn_type,
        qty=qty,
        note=note,
        created_by=user,
    )


@login_required
@role_required("keeper")
def stock_in(request):
    return _txn_create_page(request, txn_type=StockTxn.IN, title="入库")


@login_required
@role_required("keeper")
def stock_out(request):
    return _txn_create_page(request, txn_type=StockTxn.OUT, title="出库")


def _txn_create_page(request, *, txn_type: str, title: str):
    if request.method == "POST":
        form = StockTxnForm(request.POST)
        if form.is_valid():
            item = form.cleaned_data["item"]
            qty = form.cleaned_data["qty"]
            note = form.cleaned_data.get("note", "")

            try:
                _apply_txn(user=request.user, txn_type=txn_type, item=item, qty=qty, note=note)
            except ValueError as e:
                # 库存不足等业务错误
                return render(
                    request,
                    "inventory/txn_form.html",
                    {"form": form, "title": title, "error": str(e)},
                )

            return redirect("stock_list")
    else:
        form = StockTxnForm()

    return render(request, "inventory/txn_form.html", {"form": form, "title": title})