from django.contrib.auth.models import User
from django.core.management import BaseCommand
from django.db.models import Avg, Max, Min, Count, Sum

from shopapp.models import Product, Order


class Command(BaseCommand):
    def handle(self, *args, **options):
        # with transaction/atomic():
            # и так же как декоратор атомик, этот контекстный менеджер можно использовать.
        self.stdout.write("__________________________\n"
                          " Start demo aggregate !!!\n"
                          "--------------------------")

        # res = Product.objects.filter(
        #     name__contains='Smartphone',
        # ).aggregate(
        #     Avg('price'),
        #     Max('price'),
        #     # ниже то же самое, только сразу параметрам свои имена присвоили:
        #     min_price=Min('price'),
        #     count=Count('id'),
        # )
        # print(res)

        orders = Order.objects.annotate(
            total=Sum('products__price', default=0),
            products_count=Count('products'),
        )
        for order in orders:
            print(f'Order #{order.id} '
                  f'with {order.products_count} '
                  f'products worth {order.total}')


        self.stdout.write("____\n"
                          "Done\n"
                          "----")
