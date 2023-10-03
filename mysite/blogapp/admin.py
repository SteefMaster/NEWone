from django.contrib import admin
from .models import  Article
# Register your models here.
class ArticlesAdmin(admin.ModelAdmin):
    list_display = ["title", "pub_date"]


admin.site.register(Article, ArticlesAdmin)