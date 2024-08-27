from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.views.generic import ListView, DetailView
from .models import Product, Category
from ecommerce.utils import SafeGetObjectMixin


class ProductListView(ListView):
    model = Product
    template_name = 'product_list.html'
    context_object_name = 'products'


class ProductUpdateView(UserPassesTestMixin, UpdateView):
    model = Product
    fields = ['description', 'price', 'stock', 'category']
    template_name = 'update_product.html'
    success_url = reverse_lazy('product_list')

    def test_func(self):
        # only allow admin users
        return self.request.user.is_staff

    def form_valid(self, form):
        # called when form was validated successfully according to model
        # Custom form validation logic if needed
        return super().form_valid(form)

    def form_invalid(self, form):
        # called when form failed validation
        print(f"form_invalid called with form errors: {form.errors}")
        return super().form_invalid(form)


class ProductCreateView(UserPassesTestMixin, CreateView):
    model = Product
    fields = ['name', 'description', 'price', 'stock', 'category']
    template_name = 'create_product.html'
    success_url = reverse_lazy('product_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        return response

    def form_invalid(self, form):
        # Check if the form_invalid method is correctly handling errors
        print(f"form_invalid called with form errors: {form.errors}")
        return super().form_invalid(form)

    def test_func(self):
        # only allow admin users
        return self.request.user.is_staff


class BaseProductView(UserPassesTestMixin):
    model = Product
    fields = ['name', 'description', 'price', 'stock', 'category']
    success_url = reverse_lazy('product_list')

    def test_func(self):
        return self.request.user.is_staff

    def get_object(self, *args, **kwargs):
        return self.model.objects.get(pk=self.kwargs['pk'])


class ProductDeleteView(SafeGetObjectMixin, BaseProductView, DeleteView):
    template_name = 'delete_product.html'

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class ProductDetailView(SafeGetObjectMixin, BaseProductView, DetailView):
    template_name = 'product_detail.html'

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class CategoryListView(UserPassesTestMixin, ListView):
    model = Category
    template_name = 'category_list.html'
    context_object_name = 'categories'


class CategoryUpdateView(UserPassesTestMixin, UpdateView):
    model = Category
    fields = ['description']
    template_name = 'update_category'
    success_url = reverse_lazy('category_list')

    def test_func(self):
        # only allow admin users
        return self.request.user.is_staff

    def form_valid(self, form):
        # called when form was validated successfully according to model
        # Custom form validation logic if needed
        return super().form_valid(form)

    def form_invalid(self, form):
        # called when form failed validation
        print(f"form_invalid called with form errors: {form.errors}")
        return super().form_invalid(form)


class CategoryCreateView(UserPassesTestMixin, CreateView):
    model = Category
    fields = ['name', 'description']
    template_name = 'create_product.html'
    success_url = reverse_lazy('category_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        return response

    def form_invalid(self, form):
        # Check if the form_invalid method is correctly handling errors
        print(f"form_invalid called with form errors: {form.errors}")
        return super().form_invalid(form)

    def test_func(self):
        # only allow admin users
        return self.request.user.is_staff


class BaseCategoryView(UserPassesTestMixin):
    model = Category
    fields = ['name', 'description']
    success_url = reverse_lazy('category_list')

    def test_func(self):
        return self.request.user.is_staff

    def get_object(self, *args, **kwargs):
        return self.model.objects.get(pk=self.kwargs['pk'])


class CategoryDeleteView(SafeGetObjectMixin, BaseCategoryView, DeleteView):
    template_name = 'delete_category.html'

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class CategoryDetailView(SafeGetObjectMixin, BaseCategoryView, DetailView):
    template_name = 'category_detail.html'

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
