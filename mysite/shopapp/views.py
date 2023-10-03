"""
В этом модуле лежат различные наборы представлений.

Разные view для интернет-магазина: по товарам, заказам и так далее.
"""
import logging

from csv import DictWriter
from timeit import default_timer

from django.contrib.auth.models import Group, User
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.syndication.views import Feed
from django.core.cache import cache
# LoginRequiredMixin make views available only for authorized users

from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.urls import reverse_lazy

# этот декоратор позволяет декорировать методы путем передачи в него соответствующего декоратора,
# в т.ч. и в django rest_framework:
from django.utils.decorators import method_decorator

from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiResponse


from .common import save_csv_products, save_csv_orders
from .forms import ProductForm
from .models import Product, Order, ProductImage
from .serializers import ProductSerializer,  OrderSerializer

# прописываем здесь инструмент, а потом используем во въю-функциях, указывая соответствующий уровень дебаггинга.
log = logging.getLogger(__name__)


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

#    filter_backends = [
#        SearchFilter,
#        OrderingFilter,
#        DjangoFilterBackend,
#    ]

    filter_backends = [
        OrderingFilter,
        DjangoFilterBackend,
    ]
    search_fields = ["delivery_address", "products"]
    filterset_fields = [
        "delivery_address",
        "promocode",
        "created_at",
        "user",
        "products",
    ]
    ordering_fields = [
        "user",
        "created_at",
        "products"
    ]

    @extend_schema(
        summary="Get one order by ID",
        description="Retrieves **order**, returns 404 if not found",
        responses={
            200: OrderSerializer,
            404: OpenApiResponse(description="Empty response, order by id not found"),
        }
    )
    def retrieve(self, *args, **kwargs):
        return super().retrieve(*args, **kwargs)

    @action(methods=["get"], detail=False)
    def download_csv(self, request: Request):
        response = HttpResponse(content_type="text/csv")
        filename = "orders-export.csv"
        response["Content-Disposition"] = f"attachment; filename={filename}"
        queryset = self.filter_queryset(self.get_queryset())
        fields = [
            "delivery_address",
            "promocode",
            "created_at",
            "user",
            "products",
        ]
        queryset = queryset.only(*fields)
        writer = DictWriter(response, fieldnames=fields)
        writer.writeheader()

        for order in queryset:
            writer.writerow({
                field: getattr(order, field)
                for field in fields
            })

        return response

    @action(
        detail=False,
        methods=["post"],
        # по умолчанию в django выбран JsonParser, а мы установили MultiPartParcer, который позволяет парсить то что
        # мы передали в виде файлов:
        parser_classes=[MultiPartParser],
    )
    def upload_csv(self, request: Request):
        orders = save_csv_orders(
            request.FILES["file"].file,
            encoding=request.encoding,
        )
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)


# здесь будет показано как применить кэширование к странице django rest_ramework, т.к. декоратор cache_page
# в этом случае не применить ни через views ни через urls.
@extend_schema(description="Product views CRUD")
class ProductViewSet(ModelViewSet):
    """
    Набор представлений для действий над Product.
    Полный CRUD для сущностей товара.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter,
    ]
    search_fields = ["name", "description"]
    filterset_fields = [
        "name",
        "description",
        "price",
        "discount",
        "archived",
    ]
    ordering_fields = [
        "name",
        "price",
        "discount",
    ]

    @extend_schema(
        summary="Get one product by ID",
        description="Retrieves **product**, returns 404 if not found",
        responses={
            200: ProductSerializer,
            404: OpenApiResponse(description="Empty response, product by id not found"),
        }
    )
    def retrieve(self, *args, **kwargs):
        return super().retrieve(*args, **kwargs)

    @action(methods=["get"], detail=False)
    def download_csv(self, request: Request):
        response = HttpResponse(content_type="text/csv")
        filename = "products-export.csv"
        response["Content-Disposition"] = f"attachment; filename={filename}"
        queryset = self.filter_queryset(self.get_queryset())
        fields = [
            "name",
            "description",
            "price",
            "discount",
        ]
        queryset = queryset.only(*fields)
        writer = DictWriter(response, fieldnames=fields)
        writer.writeheader()

        for product in queryset:
            writer.writerow({
                field: getattr(product, field)
                for field in fields
            })

        return response

    @action(
        detail=False,
        methods=["post"],
        # по умолчанию в django выбран JsonParser, а мы установили MultiPartParcer, который позволяет парсить то что
        # мы передали в виде файлов:
        parser_classes=[MultiPartParser],
    )
    def upload_csv(self, request: Request):
        products = save_csv_products(
            request.FILES["file"].file,
            encoding=request.encoding,
        )
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    # чисто для кэширования страницы, которую представляет этот view-класс, переопределяем его родительский метод:
    # данный декоратор позволяет кэшировать отдельные методы во view-классах.
    @method_decorator(cache_page(60 * 2))
    def list(self, *args, **kwargs):
        # print('hello products list')
        return super().list(*args, *kwargs)


class ShopMainView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        context = {
            "time_running": default_timer(),
        }
        return render(request, 'shopapp/shop-main.html', context=context)


class ShopIndexView(View):

    #  можно кэшировать как с помощью декоратора method_decorator, так и непосредственно в urls. здесь у меня
    #  реализован метод кэширования view-класса на уровне urls, поэтому декоратор закомментирован.
    # @method_decorator(cache_page(60 * 5))
    def get(self, request: HttpRequest) -> HttpResponse:
        products = [
            ('Laptop', 1999),
            ('Desktop', 2999),
            ('Smartphone', 999),
        ]
        context = {
            "time_running": default_timer(),
            "products": products,
        }
        print("shop index context", context)
        log.debug('Products for shop index: %s', products)
        log.info('Rendering shop index')
        return render(request, 'shopapp/shop-index.html', context=context)


class ProductDetailsView(DetailView):
    template_name = 'shopapp/product-details.html'
    # model = Product
    queryset = Product.objects.prefetch_related('images')
    context_object_name = 'product'


class ProductsListView(ListView):
    template_name = 'shopapp/products-list.html'
    model = Product
    context_object_name = 'products'
    queryset = Product.objects.filter(archived=False)


class OrderDetailsView(LoginRequiredMixin, DetailView):
    template_name = 'shopapp/order-details.html'
    # permission_required = ['view_order']  # or u can tag ['shopapp.view_order']
    queryset = (
        Order.objects
        .select_related("user")
        .prefetch_related("products")
    )
    context_object_name = 'orders'


class OrdersListView(LoginRequiredMixin, ListView):
    # we have some dependencies in 'Order model', so we have to use querryset instead 'model = Order'
    queryset = (
        Order.objects
        .select_related("user")
        .prefetch_related("products")
    )
    context_object_name = 'orders'


class ProductCreateView(PermissionRequiredMixin, CreateView):
    permission_required = ['shopapp.add_product']
    model = Product

    # u can tag field here, if u haven't create special form in form.py

    fields = 'name', 'price', 'description', 'discount', 'preview'
    success_url = reverse_lazy('shopapp:products_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    # or u can tag:
    # form_class = ClassForm      # (ClassForm have to be already created in forms.py)


class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    # u can tag field here, if u haven't create special form in form.py
    fields = 'delivery_address', 'promocode', 'user', 'products'
    # or u can tag:
    # form_class = ClassForm      # (ClassForm have to be already created in forms.py)

    # reverse method works only from views.py, so here we have to use reverse_lazy from django.urls
    success_url = reverse_lazy('shopapp:orders_list')


class ProductUpdateView(UserPassesTestMixin, PermissionRequiredMixin, UpdateView):
    permission_required = ['shopapp.change_product']
    model = Product
    # fields = 'name', 'price', 'description', 'discount', 'preview'
    template_name_suffix = '_update_form'
    form_class = ProductForm

    def form_valid(self, form):
        response = super().form_valid(form)
        for image in form.files.getlist('images'):
            ProductImage.objects.create(
                product=self.object,
                image=image
            )
        return response

    def test_func(self):
        return self.get_object().created_by == self.request.user

    # because  back link have 'pk', we cant use 'success_url = reverse_lazy('your_adress')', and have to use
    # def get_success_url(self):
    def get_success_url(self):
        return reverse(
            'shopapp:product_details',
            kwargs={'pk': self.object.pk},
        )


class OrderUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = ['shopapp.update_order']
    model = Order
    fields = 'delivery_address', 'promocode', 'user', 'products'
    template_name_suffix = '_update_form'
    # because back link have 'pk', we cant use 'success_url = reverse_lazy('your_adress')', and have to use
    # def get_success_url(self):

    def get_success_url(self):
        return reverse(
            'shopapp:order_details',
            kwargs={'pk': self.object.pk},
        )


class ProductDeleteView(UserPassesTestMixin, PermissionRequiredMixin, DeleteView):
    permission_required = ['shopapp.delete_product']

    def test_func(self):
        return self.get_object().created_by == self.request.user

    model = Product
    success_url = reverse_lazy('shopapp:products_list')


class OrderDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = ['shopapp.delete_order']
    model = Order
    success_url = reverse_lazy('shopapp:orders_list')


class ProductArchiveView(UserPassesTestMixin, PermissionRequiredMixin, DeleteView):
    permission_required = ['shopapp.delete_product']
    model = Product
    success_url = reverse_lazy('shopapp:products_list')
    template_name_suffix = '_confirm_archive'

    def test_func(self):
        return self.get_object().created_by == self.request.user

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)


class OrdersDataExportView(UserPassesTestMixin, View):

    def test_func(self):
        if self.request.user.is_staff:
            return True

    def get(self, request: HttpRequest) -> JsonResponse:
        orders = Order.objects.order_by('pk').all()
        orders_data = [
            {
                'pk': order.pk,
                'delivery_address': order.delivery_address,
                'promocode': order.promocode,
                'user': order.user.pk,
                'products': [str(product) for product in order.products.filter().values()],
            }
            for order in orders
        ]
        return JsonResponse({'orders': orders_data})


# ----------------------------------пример низкоуровневого кэширования через Cache API:--------------------------------
# так же без прописывания каких-либо middlewares
#

class ProductsDataExportView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        cache_key = "products_data_export"
        products_data = cache.get(cache_key)
        if products_data is None:
            products = Product.objects.order_by('pk').all()
            products_data = [
                {
                    'pk': product.pk,
                    'name': product.name,
                    'price': product.price,
                    'archived': product.archived
                }
                for product in products
            ]
            elem = products_data[0]
            name = elem['name']
            cache.set(cache_key, products_data, 300)
        return JsonResponse({'products': products_data})


class LatestProductsFeed(Feed):
    title = 'Our products'
    description = 'Updates on changes or addition new product.'
    link = reverse_lazy('shopapp:products_list')

    def items(self):
        return (
            Product.objects
            .filter(archived=False)
            .order_by('created_at')
        )

    def item_title(self, item: Product):
        return item.name

    def item_description(self, item: Product):
        return item.description[:200]


class UserOrdersListView(LoginRequiredMixin, DetailView):
    template_name = 'shopapp/user_orders.html'
    model = User

    def get_queryset(self):
        q = super().get_queryset()
        try:
            self.owner = q.filter(pk=self.kwargs["pk"])[0]
        except Exception as exc:
            raise Http404('Такого пользователя не существует')
        return q

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        res = Order.objects.filter(user_id=self.owner.pk)
        context['orders'] = [order.pk for order in res]
        context['owner'] = self.owner
        context['user'] = self.request.user

        return context


class UserOrdersDataExportView(View):

    def get(self, request: HttpRequest, user_id) -> JsonResponse:
        try:
            user = User.objects.get(pk=user_id)
        except Exception as exc:
            raise Http404('Такого пользователя не существует')
        cache_key = 'user_orders_data_export'
        orders_data = cache.get(cache_key)
        if orders_data is None:
            orders = Order.objects.filter(user_id=user_id).order_by('pk')
            orders_data = [
                {
                    'pk': order.pk,
                    'delivery_address': order.delivery_address,
                    'promocode': order.promocode,
                    'user': order.user.pk,
                    'products': [str(product) for product in order.products.filter().values()],
                }
                for order in orders
            ]
            cache.set(cache_key, orders_data, 300)
        return JsonResponse({'orders': orders_data})
