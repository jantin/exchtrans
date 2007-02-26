from django.conf.urls.defaults import *
from django.contrib.auth.views import *
from exchtran.et.views import *

urlpatterns = patterns('',
	# ET Pages
	(r'^$', 'exchtran.et.views.dashboard'),
	(r'^dashboard/$', 'exchtran.et.views.dashboard'),
	(r'^monitor/$', 'exchtran.et.views.monitor'),
	(r'^editor/$', 'exchtran.et.views.editor'),
	(r'^archive/$', 'exchtran.et.views.archive'),
	(r'^users/$', 'exchtran.et.views.users'),
	
	# Registration Pages
	(r'^login/$', 'django.contrib.auth.views.login'),
	(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/login'}),
	(r'^accounts/login/$', 'django.contrib.auth.views.login'),
	(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page': '/login'}),
	(r'^accounts/profile/$', 'exchtran.et.views.profile_redirect'), # default page after login
	
	# Media Files
	(r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/Users/jonlesser/Documents/Berkeley/07Spring/ExchTrans/svn/exchtran/media'}),
	
	# Admin pages
	(r'^admin/', include('django.contrib.admin.urls')),
)
