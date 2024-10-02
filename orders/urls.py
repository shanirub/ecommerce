from django.urls import path
from .views import (
    OrderListView,
    OrderDetailView,
    OrderCreateView,
    OrderUpdateView,
    OrderDeleteView,
    OrderItemListView,
    OrderItemDetailView,
    OrderItemCreateView,
    OrderItemUpdateView,
    OrderItemDeleteView
)

urlpatterns = [
    # Order URLs
    path('', OrderListView.as_view(), name='order-list'),  # List of orders
    path('create/', OrderCreateView.as_view(), name='order-create'),  # Create a new order
    path('<int:pk>/', OrderDetailView.as_view(), name='order-detail'),  # View details of a specific order
    path('<int:pk>/update/', OrderUpdateView.as_view(), name='order-update'),  # Update an existing order
    path('<int:pk>/delete/', OrderDeleteView.as_view(), name='order-delete'),  # Delete an order

    # Order Item URLs
    path('<int:order_pk>/items/', OrderItemListView.as_view(), name='orderitem-list'),
    # List of items in a specific order
    path('<int:order_pk>/items/create/', OrderItemCreateView.as_view(), name='orderitem-create'),
    # Create a new order item
    path('<int:order_pk>/items/<int:pk>/', OrderItemDetailView.as_view(), name='orderitem-detail'),
    # View details of a specific order item
    path('<int:order_pk>/items/<int:pk>/update/', OrderItemUpdateView.as_view(), name='orderitem-update'),
    # Update an existing order item
    path('<int:order_pk>/items/<int:pk>/delete/', OrderItemDeleteView.as_view(), name='orderitem-delete'),
    # Delete an order item
]
