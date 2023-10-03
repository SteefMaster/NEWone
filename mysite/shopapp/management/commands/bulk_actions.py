from django.contrib.auth.models import User
from django.core.management import BaseCommand

from shopapp.models import Product


class Command(BaseCommand):
    def handle(self, *args, **options):
        # with transaction/atomic():
            # и так же как декоратор атомик, этот контекстный менеджер можно использовать.
        self.stdout.write("__________________________\n"
                          "Start demo bulk actions!!!\n"
                          "--------------------------")

        res = Product.objects.filter(
            name__contains='Smartphone'
        ).update(discount=11)

        print(res)

        # to create:

        # info = [
        #     # все остальные, не заданные поля, будут заданы значениями по умолчанию:
        #     ('Smartphone 1', 199, 1),
        #     ('Smartphone 2', 299, 1),
        #     ('Smartphone 3', 399, 1),
        # ]
        # products = [
        #     Product(name=name, price=price, created_by_id=by)
        #     for name, price, by in info
        # ]
        # # групповое добавление записей в таблицу через метод bulk_create():
        # res = Product.objects.bulk_create(products)
        #
        # for obj in res:
        #     print(obj)

        self.stdout.write("____\n"
                          "Done\n"
                          "----")
