from django.forms import ModelForm
from .models import OrderItem


class OrderItemForm(ModelForm):
    class Meta:
        model = OrderItem
        fields = ['quantity']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['price'].disabled = True  # Disable price editing