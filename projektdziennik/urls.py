from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from django.urls import path

# # old
# urlpatterns = [
#     url(r'^admin/', admin.site.urls),
#     url(r'^', include('edziennik.urls', namespace="edziennik")),
#     url(r'^accounts/', include('registration.backends.default.urls')),
# ]

# new
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('edziennik.urls', namespace="edziennik")),
    path('accounts/', include('registration.backends.default.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

