from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView, CreateView
from .models import Product


class ProductUpdateView(UserPassesTestMixin, UpdateView):
    model = Product
    fields = ['description', 'price', 'stock', 'category']
    template_name = 'update_product.html'
    success_url = reverse_lazy('product_list')

    def test_func(self):
        # only allow admin users
        return self.request.user.is_staff

    def form_valid(self, form):
        # Custom form validation logic if needed
        return super().form_valid(form)


class ProductCreateView(UserPassesTestMixin, CreateView):
    model = Product
    fields = ['name', 'description', 'price', 'stock', 'category']
    template_name = 'create_product.html'
    success_url = reverse_lazy('product_list')

    def form_valid(self, form):
        return super().form_valid(form)

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
