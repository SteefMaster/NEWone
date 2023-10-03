from django.shortcuts import render

from django.views.generic import ListView

from blogapp.models import Article


class ArticlesListView(ListView):
    template_name = 'blogapp/articles_list.html'
    queryset = (
        Article.objects
        .select_related("author")
        .select_related("category")
        .prefetch_related("tags")
        .defer("content")
    )
    context_object_name = 'articles'
    print(queryset)

