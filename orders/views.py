from django.views.generic import ListView, DetailView
from django.core.exceptions import ValidationError
from .models import Order, OrderItem
from core.mixins import GroupRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from ecommerce.utils import SafeGetObjectMixin
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
            # shift manager have access to all orders
            return Order.objects.all()
        # customers have access only to their orders
        return Order.objects.filter(user=self.request.user)


class OrderDetailView(GroupRequiredMixin, SafeGetObjectMixin, DetailView):
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
        raw_value = self.request.POST.get('is_paid')
        if validate_raw_bool_value(raw_value):
            return super().post(self, request, *args, **kwargs)

        raise ValidationError("is_paid field must be True or False")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class OrderUpdateView(GroupRequiredMixin, SafeGetObjectMixin, UpdateView):
    model = Order
    fields = ['is_paid']
    template_name = 'update_order.html'
    success_url = reverse_lazy('order-list')
    allowed_groups = ['customers', 'shift_manager']

    def post(self, request, *args, **kwargs):
        raw_value = self.request.POST.get('is_paid')
        if validate_raw_bool_value(raw_value):
            return super().post(self, request, *args, **kwargs)

        raise ValidationError("is_paid field must be True or False")


class OrderDeleteView(GroupRequiredMixin, SafeGetObjectMixin, DeleteView):
    model = Order
    template_name = 'delete_order.html'
    success_url = reverse_lazy('order-list')
    allowed_groups = ['customers', 'shift_manager']


''' OrderItem views'''
# TODO: create super class for OrderItem views? lots of duplicate code

class OrderItemCreateView(UserPassesTestMixin, CreateView):
    model = OrderItem
    fields = ['product', 'quantity', 'price']
    template_name = 'create_order_item.html'
    success_url = reverse_lazy('order_list')

    def form_valid(self, form):
        form.instance.order = self.get_order()  # Set the related order
        return super().form_valid(form)

    def get_order(self):
        """Helper method to get the related order"""
        return Order.objects.get(pk=self.kwargs['order_id'])

    def test_func(self):
        # Check if the user is either the order creator or a shift manager
        order = self.get_order()
        return self.request.user == order.user or is_shift_manager(self.request.user)


class OrderItemUpdateView(UserPassesTestMixin, UpdateView):
    model = OrderItem
    fields = ['quantity', 'price']
    template_name = 'update_order_item.html'
    success_url = reverse_lazy('order_list')

    def test_func(self):
        # Check if the user is either the order item creator or a shift manager
        order_item = self.get_object()
        return self.request.user == order_item.order.user or is_shift_manager(self.request.user)


class OrderItemDeleteView(SafeGetObjectMixin, UserPassesTestMixin, DeleteView):
    model = OrderItem
    template_name = 'delete_order_item.html'
    success_url = reverse_lazy('order_list')

    def test_func(self):
        # Check if the user is either the order item creator or a shift manager
        order_item = self.get_object()
        return self.request.user == order_item.order.user or is_shift_manager(self.request.user)


class OrderItemListView(ListView):
    model = OrderItem
    template_name = 'order_item_list.html'
    context_object_name = 'order_items'

    def get_queryset(self):
        # Customers can only see their own order items, while Shift Managers can see all
        if is_shift_manager(self.request.user):
            return OrderItem.objects.all()
        else:
            return OrderItem.objects.filter(order__user=self.request.user)


class OrderItemDetailView(GroupRequiredMixin, DetailView):
    model = OrderItem
    template_name = 'orders/orderitem_detail.html'
    context_object_name = 'order_item'
    allowed_groups = ['staff', 'shift_manager', 'customers']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = self.object.order
        return context

    def test_func(self):
        order_item = self.get_object()
        return super().test_func() and self.request.user in order_item.order.customers.all()
