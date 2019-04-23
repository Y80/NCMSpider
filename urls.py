from django.conf.urls import url
from django.views import static
import views


urlpatterns = [
    url(r'^$', views.index),
    url(r'^comment/?$', views.comment),
    url(r'^api/comments/?$', views.api_comments_data),
    url(r'^api/search/?$', views.api_search),
    url(r'^static/(?P<path>.*)$', static.serve, {'document_root': 'static'}),  # 引入 static 中的静态文件
]
