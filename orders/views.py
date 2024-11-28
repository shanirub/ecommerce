from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.core.exceptions import ValidationError
from django.urls import reverse_lazy

from ecommerce.management.commands.assign_permissions import logger
from products.models import Product
from .forms import OrderItemForm
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

    def get_total_price(self, order_id):
        total_price = self.model.objects.get_total_price(order_id)
        return total_price

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_price'] = self.get_total_price(self.kwargs['pk'])
        return context


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

class OrderItemCreateView(OwnershipRequiredMixin, GroupRequiredMixin, CreateView):
    model = OrderItem
    fields = ['product', 'quantity', 'price']
    template_name = 'create_order_item.html'
    allowed_groups = ['customers', 'shift_manager']

    def get_order(self):
        obj = Order.objects.get_order(self.kwargs['pk'])
        return obj

    def get_object_owner(self, **kwargs):
        """
        special case: check ownership not on associated model
            (check ownership on Order, since OrderItem was not created yet)
        override OwnershipRequiredMixin method
        """
        obj = self.get_order()
        obj_owner = obj.user
        return obj_owner

    def form_valid(self, form):
        # Associate the order item with the order instance before saving
        form.instance.order = self.get_order()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = self.get_order()  # Pass the order to the template if needed
        context['products'] = Product.objects.all()
        context['success'] = None
        context['error'] = None

        return context

    def get_success_url(self):
        return reverse_lazy('order-detail', kwargs={'pk': self.kwargs['pk']})


class OrderItemUpdateView(GroupRequiredMixin, OwnershipRequiredMixin, UpdateView):
    model = OrderItem
    # fields = ['quantity', 'price']
    form_class = OrderItemForm
    template_name = 'update_order_item.html'
    allowed_groups = ['customers', 'shift_manager']

    def get_success_url(self):
        return reverse_lazy('orderitem-detail', kwargs={'pk': self.object.pk})

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        order_item = self.get_object()

        # Fill in missing values with current object's values
        if not form.data.get('quantity'):
            form.data = form.data.copy()  # Make the QueryDict mutable
            form.data['quantity'] = order_item.quantity
        if not form.data.get('price'):
            form.data = form.data.copy()
            form.data['price'] = order_item.price

        return form

    def form_invalid(self, form):
        logger.error("Form validation failed again. Errors:", form.errors)
        context = self.get_context_data(form=form)
        context['success'] = False
        context['error'] = form.errors
        return self.render_to_response(context)

    def form_valid(self, form):
        try:
            result = OrderItem.objects.update_order_item(
                order_item_id=self.kwargs['pk'],
                **form.cleaned_data
            )
            if result is None:
                raise ValidationError(f"Couldn't update order_item #{self.kwargs['pk']}")
        except ValidationError as e:
            logger.error(f"Something went wrong with order_item #{self.kwargs['pk']} update")
            context = self.get_context_data(form=form)
            context['success'] = False
            context['error'] = form.errors
            return self.render_to_response(context)

        # TODO: quantity change for order item is not saved
        # Save the updated instance
        self.object = form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault('success', False)  # Set default for 'success'
        context.setdefault('error', None)     # Set default for 'error'
        return context


    # def form_invalid(self, form):
    #     self.extra_context = {'success': False, 'error': form.errors}
    #     return super().form_invalid(form)



class OrderItemDeleteView(GroupRequiredMixin, OwnershipRequiredMixin, DeleteView):
    model = OrderItem
    template_name = 'delete_order_item.html'
    # success_url = reverse_lazy('order-detail')
    allowed_groups = ['customers', 'shift_manager']

    def get_order_id(self):
        order = self.model.objects.get_containing_order(self.kwargs['pk'])
        return order.id

    def get_success_url(self):
        return reverse_lazy('order-detail', kwargs={'pk': self.get_order_id()})


class OrderItemDetailView(GroupRequiredMixin, OwnershipRequiredMixin, DetailView):
    model = OrderItem
    template_name = 'order_item_detail.html'
    allowed_groups = ['staff', 'shift_manager', 'customers']

