from django.contrib import admin
from django.urls import path, include
from .views import ProductUpdateView, ProductCreateView

urlpatterns = [
    path('admin/', admin.site.urls),
    #path('products/', include('products.urls')),
    path('product/update/<int:pk>/', ProductUpdateView.as_view(), name='update_product'),
    path('product/create/', ProductCreateView.as_view(), name='create_product'),
]
