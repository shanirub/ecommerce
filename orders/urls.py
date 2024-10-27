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
    path('orders/', OrderListView.as_view(), name='order-list'),
    path('orders/create/', OrderCreateView.as_view(), name='order-create'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('orders/<int:pk>/update/', OrderUpdateView.as_view(), name='order-update'),
    path('orders/<int:pk>/delete/', OrderDeleteView.as_view(), name='order-delete'),

    path('orders/<int:pk>/order-items/create/', OrderItemCreateView.as_view(), name='orderitem-create'),

    # Order Item URLs
    path('order-items/', OrderItemListView.as_view(), name='orderitem-list'),
    # path('order-items/create/', OrderItemCreateView.as_view(), name='orderitem-create'),
    path('order-items/<int:pk>/', OrderItemDetailView.as_view(), name='orderitem-detail'),
    path('order-items/<int:pk>/update/', OrderItemUpdateView.as_view(), name='orderitem-update'),
    path('order-items/<int:pk>/delete/', OrderItemDeleteView.as_view(), name='orderitem-delete'),
]

