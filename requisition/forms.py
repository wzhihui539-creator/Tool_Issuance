from django import forms
from django.forms import inlineformset_factory
from .models import Requisition, RequisitionLine

class RequisitionForm(forms.ModelForm):
    class Meta:
        model = Requisition
        fields = ["machine_no", "note"]

class RequisitionLineForm(forms.ModelForm):
    class Meta:
        model = RequisitionLine
        fields = ["item", "qty"]

    def clean_qty(self):
        qty = self.cleaned_data["qty"]
        if qty <= 0:
            raise forms.ValidationError("数量必须大于 0")
        return qty

RequisitionLineFormSet = inlineformset_factory(
    Requisition,
    RequisitionLine,
    form=RequisitionLineForm,
    extra=3,        # 默认给3行，够用；以后可改
    can_delete=True
)
