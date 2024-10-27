from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.core.exceptions import ValidationError
from django.urls import reverse_lazy
from .models import Order, OrderItem
from core.mixins import GroupRequiredMixin, OwnershipRequiredMixin
from ecommerce.utils import validate_raw_bool_value

def is_shift_manager(user):
    return user.groups.filter(name='shift_manager').exists()

''' Order views'''

class OrderListView(GroupRequiredMixin, ListView):
    model = Order
    template_name = 'order_list.html'
    context_object_name = 'orders'
    allowed_groups = ['staff', 'shift_manager', 'customers']

    def get_queryset(self):
        if is_shift_manager(self.request.user):
            # Shift managers have access to all orders
            return Order.objects.all()
        # Customers have access only to their orders
        return Order.objects.filter(user=self.request.user)


class OrderDetailView(GroupRequiredMixin, OwnershipRequiredMixin, DetailView):
    model = Order
    template_name = 'order_detail.html'
    allowed_groups = ['staff', 'shift_manager', 'customers']


class OrderCreateView(GroupRequiredMixin, CreateView):
    model = Order
    fields = []
    template_name = 'create_order.html'
    success_url = reverse_lazy('order-list')
    allowed_groups = ['customers', 'shift_manager']

    def post(self, request, *args, **kwargs):
        raw_value = request.POST.get('is_paid')
        if validate_raw_bool_value(raw_value):
            return super().post(request, *args, **kwargs)
        raise ValidationError("is_paid field must be True or False")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class OrderUpdateView(GroupRequiredMixin, OwnershipRequiredMixin, UpdateView):
    model = Order
    fields = ['is_paid']
    template_name = 'update_order.html'
    success_url = reverse_lazy('order-list')
    allowed_groups = ['customers', 'shift_manager']

    def post(self, request, *args, **kwargs):
        raw_value = request.POST.get('is_paid')
        if validate_raw_bool_value(raw_value):
            return super().post(request, *args, **kwargs)
        raise ValidationError("is_paid field must be True or False")


class OrderDeleteView(GroupRequiredMixin, OwnershipRequiredMixin, DeleteView):
    model = Order
    template_name = 'delete_order.html'
    success_url = reverse_lazy('order-list')
    allowed_groups = ['customers', 'shift_manager']


''' OrderItem views'''

class OrderItemCreateView(GroupRequiredMixin, OwnershipRequiredMixin, CreateView):
    model = OrderItem
    fields = ['product', 'quantity', 'price']
    template_name = 'create_order_item.html'
    success_url = reverse_lazy('order-list')
    allowed_groups = ['customers', 'shift_manager']

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.order_id = self.kwargs['pk']  # Use pk from the URL
        return super().form_valid(form)


class OrderItemUpdateView(GroupRequiredMixin, OwnershipRequiredMixin, UpdateView):
    model = OrderItem
    fields = ['quantity', 'price']
    template_name = 'update_order_item.html'
    success_url = reverse_lazy('order-list')
    allowed_groups = ['customers', 'shift_manager']


class OrderItemDeleteView(GroupRequiredMixin, OwnershipRequiredMixin, DeleteView):
    model = OrderItem
    template_name = 'delete_order_item.html'
    success_url = reverse_lazy('order-list')
    allowed_groups = ['customers', 'shift_manager']


class OrderItemListView(GroupRequiredMixin, OwnershipRequiredMixin, ListView):
    model = OrderItem
    template_name = 'order_item_list.html'
    context_object_name = 'order_items'
    allowed_groups = ['customers', 'staff', 'shift_manager']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order_items'] = self.get_queryset()
        return context


class OrderItemDetailView(GroupRequiredMixin, OwnershipRequiredMixin, DetailView):
    model = OrderItem
    template_name = 'order_item_detail.html'
    allowed_groups = ['staff', 'shift_manager', 'customers']

