from baton.autodiscover import admin
from django.conf.urls.i18n import i18n_patterns
from django.urls import path, include
from . import settings
from django.conf.urls.static import static,re_path
from jsl_django_sitemap.views import sitemaps
from django.contrib.sitemaps.views import sitemap
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
   openapi.Info(
      title="Yoozify API",
      default_version='v1',
      description="API Descriptions",
   ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    validators=['ssv', 'flex'],
)


urlpatterns = [
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps},name='django.contrib.sitemaps.views.sitemap'),
]

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('baton/', include('baton.urls')),
    re_path('djga/', include('google_analytics.urls')),
    path('accounts/', include('Accounts.urls')),
    path('contact-us/',include('ContactUs.urls')),
    path('ticket/',include('SupportTicket.urls')),
    path('blog/',include('Blog.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
    re_path(r'^api/doc(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
)


# handler400 = 'Accounts.views.handler400'
# handler403 = 'Accounts.views.handler403'
# handler404 = 'Accounts.views.handler404'
# handler500 = 'Accounts.views.handler500'

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


