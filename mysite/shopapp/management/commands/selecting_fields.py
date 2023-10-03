from django.contrib.auth.models import User
from django.core.management import BaseCommand

from shopapp.models import Product


class Command(BaseCommand):
    def handle(self, *args, **options):
        # with transaction/atomic():
            # и так же как декоратор атомик, этот контекстный менеджер можно использовать.
        self.stdout.write("___________________________\n"
                          "Start demo select fields!!!\n"
                          "---------------------------")

        users_info = User.objects.values_list('username', flat=True)  # если убрать флаг, то будут возвращаться кортежи.
        print(list(users_info))
        for user_info in users_info:
            print(user_info)

        # products_values = Product.objects.values('pk', 'name')
        # for p_values in products_values:
        #     print(p_values)

        self.stdout.write("____\n"
                          "Done\n"
                          "----")
