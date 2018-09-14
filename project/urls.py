from aklub.views import stat_members, stat_payments

from django.conf.urls import include
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, re_path
from django.views.i18n import JavaScriptCatalog

admin.autodiscover()

urlpatterns = [
    path('admin/passreset/', auth_views.password_reset, name='password_reset'),
    path('admin/passresetdone/', auth_views.password_reset_done, name='password_reset_done'),
    re_path(
        r'^admin/passresetconfirm/(?P<uidb64>[-\w]+)/(?P<token>[-\w]+)/$',
        auth_views.password_reset_confirm,
        name='password_reset_confirm',
    ),
    path('admin/passresetcomplete/', auth_views.password_reset_complete, name='password_reset_complete'),
    path('admin/aklub/stat-members/', stat_members, name="stat-members"),
    path('admin/aklub/stat-payments/', stat_payments, name="stat-payments"),
    path('', admin.site.urls),
    path('admin/', include("massadmin.urls")),
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('jsi18n', JavaScriptCatalog.as_view()),
    path('tinymce/', include('tinymce.urls')),
    path('admin_tools/', include('admin_tools.urls')),
    path('adminactions/', include('adminactions.urls')),
    path('advanced_filters/', include('advanced_filters.urls')),
    path('', include("aklub.urls")),
]

urlpatterns += i18n_patterns(
    path('', include("aklub.urls")),
)

try:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
except ImportError:
    pass
