from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.http import HttpResponseForbidden

from accounts.decorators import role_required
from accounts.utils import has_role
from .models import Requisition, RequisitionLine
from .forms import RequisitionForm, RequisitionLineFormSet
from .services import issue_requisition_lines

@login_required
def requisition_list(request):
    if has_role(request.user, "keeper"):
        qs = Requisition.objects.all().order_by("-created_at")
    else:
        qs = Requisition.objects.filter(requester=request.user).order_by("-created_at")
    return render(request, "requisition/requisition_list.html", {"rows": qs})

@login_required
@role_required("worker")
def requisition_create(request):
    if request.method == "POST":
        form = RequisitionForm(request.POST)
        req = Requisition(requester=request.user, status=Requisition.DRAFT)
        formset = RequisitionLineFormSet(request.POST, instance=req)

        if form.is_valid() and formset.is_valid():
            req = form.save(commit=False)
            req.requester = request.user
            req.status = Requisition.SUBMITTED
            req.submitted_at = timezone.now()
            req.save()
            formset.instance = req
            formset.save()

            # 至少要有一条有效明细
            if req.lines.count() == 0:
                req.delete()
                return render(request, "requisition/requisition_form.html", {
                    "form": form, "formset": formset, "error": "至少需要一条领用明细"
                })

            return redirect("req_list")
    else:
        form = RequisitionForm()
        req = Requisition(requester=request.user)
        formset = RequisitionLineFormSet(instance=req)

    return render(request, "requisition/requisition_form.html", {"form": form, "formset": formset})

@login_required
def requisition_detail(request, pk: int):
    req = get_object_or_404(Requisition, pk=pk)
    if not (has_role(request.user, "keeper") or req.requester_id == request.user.id):
        return HttpResponseForbidden("403 Forbidden")

    lines = req.lines.select_related("item").all()
    return render(request, "requisition/requisition_detail.html", {"req": req, "lines": lines})

@login_required
@role_required("keeper")
def requisition_issue(request, pk: int):
    req = get_object_or_404(Requisition, pk=pk)

    if req.status != Requisition.SUBMITTED:
        return HttpResponseForbidden("只能发放已提交的领用单")

    if request.method == "POST":
        lines = [(ln.item, ln.qty) for ln in req.lines.select_related("item").all()]
        if not lines:
            return render(request, "requisition/requisition_issue.html", {"req": req, "error": "领用单没有明细"})

        note = f"REQ#{req.id} 设备:{req.machine_no} 备注:{req.note}"
        try:
            issue_requisition_lines(user=request.user, lines=lines, note=note)
        except ValueError as e:
            return render(request, "requisition/requisition_issue.html", {"req": req, "error": str(e)})

        req.status = Requisition.ISSUED
        req.issued_by = request.user
        req.issued_at = timezone.now()
        req.save()

        return redirect("req_detail", pk=req.id)

    return render(request, "requisition/requisition_issue.html", {"req": req})
