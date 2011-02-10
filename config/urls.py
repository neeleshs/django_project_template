from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    # If we are in debug mode, prepend a rule to urlpatterns to serve the static media
    import re
    urlpatterns = patterns('',
        url(r'^%s/(?P<path>.*)$' % re.escape(settings.MEDIA_URL.strip('/')), 
          'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )+urlpatterns
    
