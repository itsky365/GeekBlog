# -*- coding: utf-8 -*-
from django.contrib.sitemaps import Sitemap

from geekblog.blog.models import Article
from geekblog.geekblog.constants import SYNC_STATUS


class ArticleSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.5

    def items(self):
        return Article.objects.filter(hided=False, published=True, sync_status=SYNC_STATUS.SYNCED)

    def lastmod(self, obj):
        return obj.modified_time

    def location(self, obj):
        return '/article/%s/' % obj.slug
