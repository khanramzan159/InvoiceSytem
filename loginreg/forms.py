from django import forms
from django.forms import inlineformset_factory
from .models import Invoice, Item

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['customer_name', 'address', 'gst', 'amount_paid', 'amount_due', 'note']
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'class': 'form-control'}),
            'gst': forms.NumberInput(attrs={'class': 'form-control'}),
            'amount_paid': forms.NumberInput(attrs={'class': 'form-control'}),
            'amount_due': forms.NumberInput(attrs={'class': 'form-control'}),
            'subtotal': forms.NumberInput(attrs={'class': 'form-control', 'readonly': True}),
            'gst_rate': forms.NumberInput(attrs={'class': 'form-control', 'readonly': True}),
            'all_total': forms.NumberInput(attrs={'class': 'form-control', 'readonly': True}),
        }

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['item_no', 'item_name', 'quantity', 'price']
        widgets = {
            'item_no': forms.TextInput(attrs={'class': 'form-control'}),
            'item_name': forms.Textarea(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'total': forms.NumberInput(attrs={'class': 'form-control', 'readonly': True}),
            'invoice': forms.Select(attrs={'class': 'form-control'}),
            'remove': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

ItemFormSet = inlineformset_factory(
    Invoice, Item, form=ItemForm,
    extra=1, can_delete=True,
    can_delete_extra=True
)
