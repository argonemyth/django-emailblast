from django.conf.urls import patterns, include, url 

urlpatterns = patterns('emailblast.views',
    url(r'^email/(?P<slug>[-\w]+)/$',
        'view_email', name='view_email'),
    url(r'^preview/(?P<id>\d+)/(?P<format>[-\w]+)/$',
        'email_preview', name='email_preview'),
)
