from django.contrib.syndication.views import Feed
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.urls import reverse, reverse_lazy

from .models import Article


class ArticlesListView(ListView):
    template_name = 'RSS/articles_list.html'
    queryset = (
        Article.objects
        .filter(published_at__isnull=False)  # здесь через __ передается фильтрация isnull=False для поля published_at
        .order_by('-published_at')
    )


class ArticleDetailView(DetailView):
    model = Article


class LatestArticlesFeed(Feed):
    title = 'Our latest RSS articles'
    description = 'Updates on changes and addition new articles.'
    link = reverse_lazy('rss:articles')

    def items(self):
        return (
            Article.objects
            .filter(published_at__isnull=False)  # здесь через __ передается фильтрация isnull=False для поля published_at
            .order_by('-published_at')[:5]
        )

    def item_title(self, item: Article):
        return item.title

    def item_description(self, item: Article):
        return item.body[:200]

    # закоментили, потому что в саму модель Article добавили метод get_absolute_url
    # def item_link(self, item: Article):
    #     return reverse('rss:article', kwargs={'pk': item.pk})
