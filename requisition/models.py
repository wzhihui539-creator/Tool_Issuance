from django.db import models
from django.conf import settings
from inventory.models import Item

class Requisition(models.Model):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    ISSUED = "ISSUED"
    CANCELLED = "CANCELLED"

    STATUS_CHOICES = [
        (DRAFT, "草稿"),
        (SUBMITTED, "已提交"),
        (ISSUED, "已发放"),
        (CANCELLED, "已取消"),
    ]

    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="requisitions"
    )
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=DRAFT)

    machine_no = models.CharField("设备号", max_length=64, blank=True)
    note = models.CharField("用途/备注", max_length=200, blank=True)

    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    submitted_at = models.DateTimeField("提交时间", null=True, blank=True)

    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="issued_requisitions"
    )
    issued_at = models.DateTimeField("发放时间", null=True, blank=True)

    def __str__(self):
        return f"REQ#{self.id} {self.get_status_display()}"

class RequisitionLine(models.Model):
    requisition = models.ForeignKey(Requisition, on_delete=models.CASCADE, related_name="lines")
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    qty = models.PositiveIntegerField("数量")

    def __str__(self):
        return f"{self.item.code} x {self.qty}"
