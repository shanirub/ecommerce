from django.contrib import admin
from django.urls import path, include
from .views import ProductUpdateView, ProductCreateView, ProductListView, ProductDetailView, ProductDeleteView

urlpatterns = [
    path('product/update/<int:pk>/', ProductUpdateView.as_view(), name='update_product'),
    path('product/create/', ProductCreateView.as_view(), name='create_product'),
    path('product/list', ProductListView.as_view(), name='product_list'),
    path('product/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('product/<int:pk>/delete', ProductDeleteView.as_view(), name='delete_product'),
]
