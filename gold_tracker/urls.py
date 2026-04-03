from django.urls import path, include
from django.views.generic import TemplateView
from api import views as api_views

urlpatterns = [
    path('api/', include('api.urls')),
    path('favicon.webp', api_views.favicon, name='favicon_webp'),
    path('favicon.ico', api_views.favicon, name='favicon_ico'),
    path('robots.txt', api_views.robots_txt, name='robots_txt'),
    path('sitemap.xml', api_views.sitemap_xml, name='sitemap_xml'),
    path('', TemplateView.as_view(template_name='index.html'), name='index'),
    ]
