from django.conf.urls.defaults import *
from django.contrib.auth.views import *
from exchtran.et.views import *

urlpatterns = patterns('',
	# ET Admin Pages
	(r'^$', 'exchtran.et.views.dashboard'),
	(r'^dashboard/$', 'exchtran.et.views.dashboard'),
	(r'^dashboard/monitor/$', 'exchtran.et.views.monitor'),

	(r'^experiments/$', 'exchtran.et.views.experiments'),
	(r'^experiments/view/$', 'exchtran.et.views.viewExperiment'),				
	(r'^experiments/edit/$', 'exchtran.et.views.edit'),
	(r'^experiments/edit/addComponent/$', 'exchtran.et.views.addComponent'),	
	(r'^experiments/edit/newExperiment/$', 'exchtran.et.views.newExperiment'),	
	(r'^experiments/newSession/$', 'exchtran.et.views.newSession'),	

	(r'^users/$', 'exchtran.et.views.users'),

	#Deprecated
	(r'^editor/$', 'exchtran.et.views.editor'),	
	
	# ET Experiment Session Pages
	(r'^session/join/$', 'exchtran.et.views.joinSession'),
	(r'^session/wait/$', 'exchtran.et.views.wait'),
	(r'^session/start/$', 'exchtran.et.views.startSession'),
	(r'^session/stop/$', 'exchtran.et.views.stopSession'),	
	(r'^session/drive/$', 'exchtran.et.views.driveSession'),
			
	# Registration Pages
	(r'^login/$', 'django.contrib.auth.views.login'),
	(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/login'}),
	(r'^accounts/login/$', 'django.contrib.auth.views.login'),
	(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page': '/login'}),
	(r'^accounts/profile/$', 'exchtran.et.views.profile_redirect'), # default page after login
	
	# Rex: Reciprocal Exchange
	(r'^rexOffer/$', 'exchtran.et.views.rexOffer'),
	(r'^rexOffer/submit/$', 'exchtran.et.views.rexOfferSubmit'),
	(r'^rex/wait/$', 'exchtran.et.views.rexWait'),
	(r'^rex/reconcile/$', 'exchtran.et.views.rexReconcile'),
	(r'^rex/CheckAllOffered/$', 'exchtran.et.views.rexCheckAllOffered'),
	
	# API
	(r'^api/sessionStatus/$', 'exchtran.et.api.sessionStatus'),
		
	# Media Files
	(r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/Users/jonlesser/Documents/Berkeley/07Spring/ExchTrans/svn/exchtran/media'}),
	
	# Admin pages
	(r'^admin/', include('django.contrib.admin.urls')),
)
