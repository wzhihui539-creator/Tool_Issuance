from django import forms
from .models import Item, StockTxn

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ["code", "name", "spec", "unit", "category", "location", "min_stock", "is_controlled", "is_active"]

class StockTxnForm(forms.ModelForm):
    class Meta:
        model = StockTxn
        fields = ["item", "qty", "note"]

    def clean_qty(self):
        qty = self.cleaned_data["qty"]
        if qty <= 0:
            raise forms.ValidationError("数量必须大于 0")
        return qty