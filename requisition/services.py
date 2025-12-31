from django.db import transaction
from inventory.models import Stock, StockTxn, Item

@transaction.atomic
def issue_requisition_lines(*, user, lines, note: str):
    """
    lines: iterable of (item, qty)
    """
    for item, qty in lines:
        stock, _ = Stock.objects.select_for_update().get_or_create(item=item, defaults={"qty": 0})
        if stock.qty < qty:
            raise ValueError(f"库存不足：{item.code} 当前 {stock.qty}，需要 {qty}")

        stock.qty -= qty
        stock.save()

        StockTxn.objects.create(
            item=item,
            txn_type=StockTxn.OUT,
            qty=qty,
            note=note,
            created_by=user,
        )
