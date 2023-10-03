from django.urls import path, include
from django.views.decorators.cache import cache_page


from rest_framework.routers import DefaultRouter


from .views import (
    ShopIndexView,
    ProductsListView,
    ProductDetailsView,
    ProductCreateView,
    ProductUpdateView,
    ProductDeleteView,
    ProductArchiveView,
    ProductsDataExportView,
    ProductViewSet,
    OrdersListView,
    OrderDetailsView,
    OrderCreateView,
    OrderUpdateView,
    OrderDeleteView,
    OrdersDataExportView,
    OrderViewSet,
    LatestProductsFeed,
    UserOrdersListView,
    UserOrdersDataExportView,
)

app_name = "shopapp"

routers = DefaultRouter()
routers.register('products', ProductViewSet)
routers.register('orders', OrderViewSet)

urlpatterns = [
    # здесь пример применения декоратора cache_page к view-классу:
    # path("", cache_page(60 * 3)(ShopIndexView.as_view()), name="index"),

    path("", ShopIndexView.as_view(), name="index"),


    path('api/', include(routers.urls)),
    path("products/", ProductsListView.as_view(), name="products_list"),
    path("products/<int:pk>/", ProductDetailsView.as_view(), name="product_details"),
    path('products/create/', ProductCreateView.as_view(), name='product_create'),
    path("products/<int:pk>/update/", ProductUpdateView.as_view(), name="product_update"),
    path("products/<int:pk>/delete/", ProductDeleteView.as_view(), name="product_delete"),
    path("products/<int:pk>/archive/", ProductArchiveView.as_view(), name="product_archive"),
    path("products/export/", ProductsDataExportView.as_view(), name="products-export"),

    path('products/feed/', LatestProductsFeed(), name='products-feed'),

    path("orders/", OrdersListView.as_view(), name="orders_list"),
    path("orders/<int:pk>/", OrderDetailsView.as_view(), name="order_details"),
    path("orders/create/", OrderCreateView.as_view(), name="order_create"),
    path("orders/<int:pk>/update/", OrderUpdateView.as_view(), name="order_update"),
    path("orders/<int:pk>/delete/", OrderDeleteView.as_view(), name="order_delete"),
    path("orders/export/", OrdersDataExportView.as_view(), name="orders-export"),

    path("users/<int:pk>/orders/", UserOrdersListView.as_view(), name="user_orders"),
    path("users/<int:user_id>/orders/export/", UserOrdersDataExportView.as_view(), name="user_orders_export")
]
