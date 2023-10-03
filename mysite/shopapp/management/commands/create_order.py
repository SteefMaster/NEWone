from typing import Sequence

from django.contrib.auth.models import User
from django.core.management import BaseCommand
from django.db import transaction

from shopapp.models import Order, Product


class Command(BaseCommand):
    @transaction.atomic
    def handle(self, *args, **options):
        # with transaction/atomic():
            # и так же как декоратор атомик, этот контекстный менеджер можно использовать.
        self.stdout.write("Create order")
        user = User.objects.get(username="steef")
        # products: Sequence[Product] = Product.objects.defer('description', 'price', 'created_at').all()
        products: Sequence[Product] = Product.objects.only('id', 'name', 'discount', 'created_by_id', 'archived').all()
        order, created = Order.objects.get_or_create(
            delivery_address="Kazino777, azino 18",
            promocode="promo5",
            user=user,
        )
        for product in products:
            # вот такой записью мы добавляем в заказ продуты:
            if not product.archived:
                order.products.add(product)
        order.save()
        self.stdout.write(f"Created order {order}")
