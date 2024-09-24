from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.views.generic import ListView, DetailView
from .models import Order, OrderItem
from ecommerce.utils import SafeGetObjectMixin
from core.mixins import GroupRequiredMixin


class OrderListView(GroupRequiredMixin, ListView):
    model = Order
    template_name = 'order_list.html'
    context_object_name = 'orders'
    allowed_groups = ['staff', 'shift_manager', 'customers']


class OrderDetailView(GroupRequiredMixin, SafeGetObjectMixin, DetailView):
    model = Order
    template_name = 'order_detail.html'
    allowed_groups = ['staff', 'shift_manager', 'customers']


class OrderCreateView(GroupRequiredMixin, CreateView):
    model = Order
    fields = []
    template_name = 'create_order.html'
    success_url = reverse_lazy('order_list')
    allowed_groups = ['customers']

    def form_valid(self, form):
        form.instance.user = self.request.user  # Set the user to the logged-in user
        return super().form_valid(form)


class OrderUpdateView(GroupRequiredMixin, UpdateView):
    model = Order
    fields = ['is_paid']
    template_name = 'update_order.html'
    success_url = reverse_lazy('order_list')
    allowed_groups = ['staff', 'shift_manager']


class OrderDeleteView(GroupRequiredMixin, SafeGetObjectMixin, DeleteView):
    model = Order
    template_name = 'delete_order.html'
    success_url = reverse_lazy('order_list')
    allowed_groups = ['staff', 'shift_manager']


class OrderItemListView(GroupRequiredMixin, ListView):
    model = OrderItem
    template_name = 'order_item_list.html'
    context_object_name = 'order_items'
    allowed_groups = ['staff', 'shift_manager']

    def get_queryset(self):
        return OrderItem.objects.filter(order__user=self.request.user)  # Adjust based on user permissions
