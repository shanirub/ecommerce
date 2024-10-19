from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.views.generic import ListView, DetailView
from .models import Product, Category
from core.mixins import GroupRequiredMixin, SafeGetObjectMixin


class ProductListView(ListView):
    model = Product
    template_name = 'product_list.html'
    context_object_name = 'products'


class ProductUpdateView(GroupRequiredMixin, UpdateView):
    model = Product
    fields = ['description', 'price', 'stock', 'category']
    template_name = 'update_product.html'
    success_url = reverse_lazy('product_list')
    allowed_groups = ['staff', 'stock_personnel', 'shift_manager']

    def test_func(self):
        user = self.request.user
        return user.groups.filter(name__in=self.allowed_groups).exists() or user.is_superuser

    def form_valid(self, form):
        # called when form was validated successfully according to model
        # Custom form validation logic if needed
        return super().form_valid(form)

    def form_invalid(self, form):
        # called when form failed validation
        print(f"form_invalid called with form errors: {form.errors}")
        return super().form_invalid(form)


class ProductCreateView(GroupRequiredMixin, CreateView):
    model = Product
    fields = ['name', 'description', 'price', 'stock', 'category']
    template_name = 'create_product.html'
    success_url = reverse_lazy('product_list')
    allowed_groups = ['staff', 'shift_manager']

    def form_valid(self, form):
        response = super().form_valid(form)
        return response

    def form_invalid(self, form):
        # Check if the form_invalid method is correctly handling errors
        print(f"form_invalid called with form errors: {form.errors}")
        return super().form_invalid(form)

    def test_func(self):
        user = self.request.user
        return user.groups.filter(name__in=self.allowed_groups).exists() or user.is_superuser


class BaseProductView(GroupRequiredMixin):
    model = Product
    fields = ['name', 'description', 'price', 'stock', 'category']
    success_url = reverse_lazy('product_list')


class ProductDeleteView(SafeGetObjectMixin, BaseProductView, DeleteView):
    template_name = 'delete_product.html'
    allowed_groups = ['staff', 'shift_manager']

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class ProductDetailView(SafeGetObjectMixin, BaseProductView, DetailView):
    template_name = 'product_detail.html'
    allowed_groups = ['staff', 'shift_manager', 'customers', 'stock_personnel']

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class CategoryListView(ListView):
    model = Category
    template_name = 'category_list.html'
    context_object_name = 'categories'


class CategoryUpdateView(GroupRequiredMixin, UpdateView):
    model = Category
    fields = ['description']
    template_name = 'update_category.html'
    success_url = reverse_lazy('category_list')
    allowed_groups = ['staff', 'shift_manager']

    def test_func(self):
        user = self.request.user
        return user.groups.filter(name__in=self.allowed_groups).exists() or user.is_superuser

    def form_valid(self, form):
        # called when form was validated successfully according to model
        # Custom form validation logic if needed
        return super().form_valid(form)

    def form_invalid(self, form):
        # called when form failed validation
        print(f"form_invalid called with form errors: {form.errors}")
        return super().form_invalid(form)


class CategoryCreateView(GroupRequiredMixin, CreateView):
    model = Category
    fields = ['name', 'description']
    template_name = 'create_category.html'
    success_url = reverse_lazy('category_list')
    allowed_groups = ['staff', 'shift_manager']

    def form_valid(self, form):
        response = super().form_valid(form)
        return response

    def form_invalid(self, form):
        print(f"form_invalid called with form errors: {form.errors}")
        return super().form_invalid(form)

    def test_func(self):
        user = self.request.user
        return user.groups.filter(name__in=self.allowed_groups).exists() or user.is_superuser


class BaseCategoryView(GroupRequiredMixin):
    model = Category
    fields = ['name', 'description']
    success_url = reverse_lazy('category_list')

    def test_func(self):
        user = self.request.user
        return user.groups.filter(name__in=self.allowed_groups).exists() or user.is_superuser


class CategoryDeleteView(SafeGetObjectMixin, BaseCategoryView, DeleteView):
    template_name = 'delete_category.html'
    allowed_groups = ['staff', 'shift_manager']

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class CategoryDetailView(SafeGetObjectMixin, BaseCategoryView, DetailView):
    template_name = 'category_detail.html'
    allowed_groups = ['staff', 'shift_manager', 'customers', 'stock_personnel']

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
