from string import ascii_letters
from random import choices

from django.conf import settings
from django.contrib.auth.models import User, Group, Permission
from django.test import TestCase
from django.urls import reverse

from .models import Product, Order


class ProductCreateViewTestCase(TestCase):
    def setUp(self) -> None:
        self.product_name = ''.join(choices(ascii_letters, k=10))
        Product.objects.filter(name=self.product_name).delete()

    def test_product_create_view(self):
        User.objects.create_superuser(username='testuser', password='12345')
        login = self.client.login(username='testuser', password='12345')

        response = self.client.post(
            reverse('shopapp:product_create'),
            {"name": self.product_name,
             "price": '123.45',
             "description": 'A good table',
             "discount": '10'}

        )
        self.assertRedirects(response, reverse('shopapp:products_list'))
        self.assertTrue(Product.objects.filter(name=self.product_name).exists())


class ProductDetailsViewTestCase(TestCase):

    # This kind of code useful, when u create many tests inside this class (ProductDetailsViewTestCase), and instance
    # WILL BE CHANGED in concrete test (test_get_product), but in next test (test_get_product_and_get_content),
    # u need reconfigured model:

    # setUp method describes code, which will run before this test (def test_product_details_view):
    def setUp(self) -> None:
        self.product = Product.objects.create(name='Some Kind of Test product')

    # tearDown method describes actions, which will do after your test (def test_product_details_view),
    # even test will fail:
    def tearDown(self) -> None:
        self.product.delete()

    # This kind of code useful, when u create many tests inside this class (ProductDetailsViewTestCase), and instance
    # will NOT be changed in concrete test (test_get_product), and for next test (test_get_product_and_get_content),
    # u will have the same configured model (instances will create only 1 time for all tests in this class):
    # @classmethod
    # def setUpClass(cls) -> None:
    #     super().setUpClass()  # very important, because your def setUpClass(cls) method override super() methods
    #     cls.product = Product.objects.create(name='Some Kind of Test product')
    #
    # @classmethod
    # def tearDownClass(cls) -> None:
    #     super().tearDownClass()  # very important, because your def tearDownClass(cls) method override super() methods
    #     cls.product.delete()

    def test_get_product(self):
        response = self.client.get(reverse('shopapp:product_details', kwargs={'pk': self.product.pk}))
        self.assertEqual(response.status_code, 200)

    def test_get_product_and_get_content(self):
        response = self.client.get(reverse('shopapp:product_details', kwargs={'pk': self.product.pk}))
        self.assertContains(response, self.product.name)
        # self.assertContains() check response.status_code inside by default


class ProductsListViewTestCase(TestCase):
    fixtures = [
        'products-fixtures.json'
    ]

    def test_products(self):
        response = self.client.get(reverse('shopapp:products_list'))
        # this variant is the same is:
        self.assertQuerysetEqual(
            qs=Product.objects.filter(archived=False).all(),  # expected data
            values=(p.pk for p in response.context['products']),  # received data
            transform=lambda p: p.pk  # method of transforming data from qs, for compare become possible
        )
        self.assertTemplateUsed(response, "shopapp/products-list.html")  # this string checks, what template was used

        # this variant:
        product_from_db = Product.objects.filter(archived=False).all()
        product_from_context = response.context['products']  # look context_object_name in ProductsListView(ListView):
        for p_db, p_cntxt in zip(product_from_db, product_from_context):
            self.assertEqual(p_db.pk, p_cntxt.pk)

        # and this variant:
        # for product in Product.objects.filter(archived=False).all():  # speaker says, that this code-string have
        #     # to end .all(), but i dont know why.
        #     self.assertContains(response, product.name)
        # ________________________________________________


class OrdersListViewTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # cls.credentials = dict(username='tester', password='tester999')  # variant without using force_login()
        # cls.user = User.objects.create_user(**cls.credentials)  # variant without using force_login()
        cls.user = User.objects.create_user(username='tester', password='tester999')

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.user.delete()

    def setUp(self):
        # self.client.login(**self.credentials)  # variant without using force_login()
        self.client.force_login(self.user)

    def test_orders_view(self):
        response = self.client.get(reverse('shopapp:orders_list'))
        self.assertContains(response, 'Orders')

    def test_orders_view_not_authenticated(self):
        self.client.logout()
        response = self.client.get(reverse('shopapp:orders_list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)  # str() needs, because LOGIN_URL in settings.py,
        # working through reverse_lasy(), not reverse().


class OrdersExportTestCase(TestCase):
    fixtures = [
        'products-fixtures.json',
        'orders-fixtures.json',
        'users-fixtures.json',
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Jora_tester', password='pedro999')
        cls.user.is_staff = True
        group, created = Group.objects.get_or_create(
            name='shopapp_admin')
        cls.user.groups.add(group)
        cls.user.save()
        cls.maxDiff = None

    def setUp(self):
        self.client.force_login(self.user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.user.delete()

    def test_orders_export(self):
        response = self.client.get(reverse('shopapp:orders-export'))
        self.assertEqual(response.status_code, 200)
        orders = Order.objects.order_by('pk').all()
        expected_data = [
            {
                'pk': order.pk,
                'delivery_address': order.delivery_address,
                'promocode': order.promocode,
                'user': order.user.pk,
                'products': [str(product) for product in order.products.filter().values()],

            }
            for order in orders
        ]
        orders_data = response.json()
        self.assertEqual(orders_data['orders'], expected_data)


class ProductsExportViewTestCase(TestCase):
    fixtures = [
        'products-fixtures.json'
    ]

    def test_get_products_view(self):
        response = self.client.get(reverse('shopapp:products-export'))
        self.assertEqual(response.status_code, 200)
        products = Product.objects.order_by('pk').all()
        expected_data = [
            {
                'pk': product.pk,
                'name': product.name,
                'price': str(product.price),
                'archived': product.archived
            }
            for product in products
        ]
        products_data = response.json()
        self.assertEqual(products_data['products'], expected_data)


class OrderDetailsViewTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Petya_tester', password='pedro999')
        group, created = Group.objects.get_or_create(
            name='shopapp_admin')
        cls.user.groups.add(group)
        cls.user.save()

    def setUp(self) -> None:
        self.client.force_login(self.user)
        products = Product.objects.order_by('pk').all()
        self.order = Order.objects.create(
            pk='10000',
            delivery_address='Curupa str 15, 9/18 add 03',
            promocode='piece-cake',
            user=self.user,
        )

    def tearDown(self) -> None:
        self.order.delete()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.user.delete()

    def test_order_details_view(self):
        response = self.client.get(reverse('shopapp:order_details', kwargs={'pk': 10000}, ))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.order.delivery_address)
        self.assertContains(response, self.order.promocode)
        order_from_db = Order.objects.filter(pk=10000).all()
        order_from_context = response.context['orders']
        self.assertEqual(order_from_db[0].pk, order_from_context.pk)
