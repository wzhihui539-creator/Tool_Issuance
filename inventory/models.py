from django.db import models
from django.conf import settings

class Item(models.Model):
    code = models.CharField("编码", max_length=64, unique=True)
    name = models.CharField("名称", max_length=128)
    spec = models.CharField("规格/型号", max_length=128, blank=True)
    unit = models.CharField("单位", max_length=16, default="pcs")
    category = models.CharField("分类", max_length=64, blank=True)
    location = models.CharField("库位", max_length=64, blank=True)
    min_stock = models.PositiveIntegerField("最低库存", default=0)
    is_controlled = models.BooleanField("受控物料", default=False)
    is_active = models.BooleanField("启用", default=True)

    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} - {self.name}"

class Stock(models.Model):
    item = models.OneToOneField("Item", on_delete=models.CASCADE, related_name="stock")
    qty = models.IntegerField("当前库存", default=0)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    def __str__(self):
        return f"{self.item.code} qty={self.qty}"


class StockTxn(models.Model):
    IN = "IN"
    OUT = "OUT"
    ADJUST = "ADJ"

    TXN_TYPES = [
        (IN, "入库"),
        (OUT, "出库"),
        (ADJUST, "调整"),
    ]

    item = models.ForeignKey("Item", on_delete=models.PROTECT, related_name="txns")
    txn_type = models.CharField("类型", max_length=4, choices=TXN_TYPES)
    qty = models.PositiveIntegerField("数量")  # 一律正数：方向由 txn_type 决定
    note = models.CharField("备注", max_length=200, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.txn_type} {self.item.code} x {self.qty}"

