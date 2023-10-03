from random import random

from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LogoutView
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, CreateView, UpdateView, ListView, DetailView
from django.views.decorators.cache import cache_page

from .models import Profile, User

from .forms import MyAuthForm


class UsersListView(ListView):
    model = User
    context_object_name = 'users'
    template_name = 'myauth/users-list.html'


class UserDetailsView(DetailView, UserPassesTestMixin):
    template_name = 'myauth/user-details.html'
    model = User
    form_class = MyAuthForm
    context_object_name = 'user'

    def test_func(self):
        if self.request.user.is_staff or self.request.user.pk == self.model.pk:
            return True

    def dispatch(self, request, *args, **kwargs):
        self.obj_id = kwargs.get('pk')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model_instance = Profile.objects.get(user_id=self.obj_id)
        context['obj'] = model_instance
        context['form'] = self.form_class
        return context

    def post(self, request, *args, **kwargs):
        obj = Profile.objects.get(user_id=self.obj_id)
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            image = form.cleaned_data.get('avatar')
            obj.avatar = image
            obj.save()
            return redirect(
                'myauth:user-details',
                pk=obj.user_id,
            )


class AboutMeView(TemplateView):
    model = Profile
    template_name = "myauth/about-me.html"
    form_class = MyAuthForm
    success_url = reverse_lazy('myauth:about-me')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            model_instance = Profile.objects.get(user_id=self.request.user.pk)
            context['obj'] = model_instance
        except Exception as exc:
            context['obj'] = None
        context['form'] = self.form_class
        return context

    def post(self, request, *args, **kwargs):
        obj = Profile.objects.get(user_id=request.user.pk)
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            image = form.cleaned_data.get('avatar')
            obj.avatar = image
            obj.save()
            return redirect('myauth:about-me')


class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = "myauth/register.html"
    success_url = reverse_lazy("myauth:about-me")

    def form_valid(self, form):
        response = super().form_valid(form)
        Profile.objects.create(user=self.object)
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password1")
        user = authenticate(
            self.request,
            username=username,
            password=password,
        )
        login(request=self.request, user=user)
        return response


class MyLogoutView(LogoutView):
    next_page = reverse_lazy("myauth:login")


@user_passes_test(lambda u: u.is_superuser)
def set_cookie_view(request: HttpRequest) -> HttpResponse:
    response = HttpResponse("Cookie set")
    response.set_cookie("fizz", "buzz", max_age=3600)
    return response


# для декоратора cache_page не нужны никакие middlewares, он робит как отдельный способ кэширования, не зависимо от них.
# в таком виде он применяется только к view-функциям, для view-класса придется добавить кэширование всех методов в urls.
@cache_page(60 * 2)  # аргумент - время жизни кэша в секундах
def get_cookie_view(request: HttpRequest) -> HttpResponse:
    value = request.COOKIES.get("fizz", "default value")
    return HttpResponse(f"Cookie value: {value!r} + {random()}")


@permission_required("myauth.view_profile", raise_exception=True)
def set_session_view(request: HttpRequest) -> HttpResponse:
    request.session["foobar"] = "spameggs"
    return HttpResponse("Session set!")


@login_required
def get_session_view(request: HttpRequest) -> HttpResponse:
    value = request.session.get("foobar", "default")
    return HttpResponse(f"Session value: {value!r}")


class FooBarView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        return JsonResponse({'foo': 'bar', 'spam': 'eggs'})
