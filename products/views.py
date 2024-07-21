from django.shortcuts import render
from .models import Product


def update_product_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        category = request.POST.get('category')

        product = Product.objects.update_product(
            name, description=description, price=price, category=category, stock=stock)

        if product:
            # Handle success
            return render(request, 'update_product.html', {'product': product, 'success': True})
        else:
            # Handle product not found
            return render(request, 'update_product.html', {'error': 'Product not found'})

    return render(request, 'update_product.html')
