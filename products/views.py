from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView, CreateView
from django.views.generic import ListView
from .models import Product


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




# def update_product_view(request):
#     if request.method == 'POST':
#         name = request.POST.get('name')
#         description = request.POST.get('description')
#         price = request.POST.get('price')
#         stock = request.POST.get('stock')
#         category = request.POST.get('category')
#
#         product = Product.objects.update_product(
#             name, description=description, price=price, category=category, stock=stock)
#
#         if product:
#             # Handle success
#             return render(request, 'update_product.html', {'product': product, 'success': True})
#         else:
#             # Handle product not found
#             return render(request, 'update_product.html', {'error': 'Product not found'})
#
#     return render(request, 'update_product.html')
