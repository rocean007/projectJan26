from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('api/', include('api.urls')),
    path('', TemplateView.as_view(template_name='index.html'), name='index'),
    path('favicon.webp', RedirectView.as_view(url=settings.STATIC_URL + 'favicon.webp', permanent=True)),
]
