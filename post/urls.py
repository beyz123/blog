from django.urls import re_path as url, path

from . import views
from .views import *
from .views import (
        post_like
)

app_name = 'post'

urlpatterns = [
    url(r'^index/$', post_index, name='index'),
    url(r'^my_posts/$', my_posts, name='my_posts'),
    url(r'^create/$', post_create, name='create'),
    url(r'^(?P<slug>[\w-]+)/detail/$', post_detail, name='detail'),
    url(r'^(?P<slug>[\w-]+)/update/$', post_update, name='update'),
    url(r'^(?P<slug>[\w-]+)/delete/$', post_delete, name='delete'),
    url(r'^post_like/$', post_like, name='post_like'),
]
