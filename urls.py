from django.conf.urls.defaults import *
from django.contrib.auth.views import *
from exchtran.et.views import *

urlpatterns = patterns('',
	# ET Admin Pages
	(r'^$', 'exchtran.et.views.sessions'),
	(r'^sessions/$', 'exchtran.et.views.sessions'),
	(r'^sessions/monitor/$', 'exchtran.et.views.monitor'),

	(r'^experiments/$', 'exchtran.et.views.experiments'),
	(r'^experiments/view/$', 'exchtran.et.views.viewExperiment'),				
	(r'^experiments/edit/$', 'exchtran.et.views.edit'),
	(r'^experiments/edit/addComponent/$', 'exchtran.et.views.addComponent'),
	(r'^experiments/edit/removeComponent/$', 'exchtran.et.views.removeComponent'),
	(r'^experiments/edit/updateExperimentName/$', 'exchtran.et.views.updateExperimentName'),
	(r'^experiments/edit/updateExperimentDescription/$', 'exchtran.et.views.updateExperimentDescription'),	
	(r'^experiments/edit/newExperiment/$', 'exchtran.et.views.newExperiment'),	
	(r'^experiments/delete/$', 'exchtran.et.views.experimentDelete'),
	(r'^experiments/newSession/$', 'exchtran.et.views.newSession'),
	
	(r'^components/$', 'exchtran.et.views.components'),
	(r'^components/create/$', 'exchtran.et.views.componentCreate'),
	(r'^components/edit/$', 'exchtran.et.views.componentEdit'),
	(r'^components/delete/$', 'exchtran.et.views.componentDelete'),

	(r'^users/$', 'exchtran.et.views.users'),
	
	(r'^scratch/$', 'exchtran.et.views.scratch'),

	#Deprecated
	(r'^editor/$', 'exchtran.et.views.editor'),	
	
	# ET Experiment Session Pages
	(r'^session/join/$', 'exchtran.et.views.joinSession'),
	(r'^session/wait/$', 'exchtran.et.views.wait'),
	(r'^session/start/$', 'exchtran.et.views.startSession'),
	(r'^session/stop/$', 'exchtran.et.views.stopSession'),	
	(r'^session/drive/$', 'exchtran.et.views.driveSession'),
	(r'^session/delete/$', 'exchtran.et.views.deleteSession'),
	(r'^session/end/$', 'exchtran.et.views.endSession'),
	(r'^session/bootParticipant/$', 'exchtran.et.views.bootParticipant'),
	(r'^session/booted/$', 'exchtran.et.views.booted'),
			
	# Registration Pages
	(r'^login/$', 'django.contrib.auth.views.login'),
	(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/login'}),
	(r'^accounts/login/$', 'django.contrib.auth.views.login'),
	(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page': '/login'}),
	(r'^accounts/profile/$', 'exchtran.et.views.profile_redirect'), # default page after login
	
	# Text Page
	(r'^textPage/display/$', 'exchtran.et.textPage.textPageDisplay'),
	(r'^textPage/submit/$', 'exchtran.et.textPage.textPageEdit'),
	
	# Rex: Reciprocal Exchange
	(r'^rexOffer/$', 'exchtran.et.views.rexOffer'),
	(r'^rexOffer/submit/$', 'exchtran.et.views.rexOfferSubmit'),
	(r'^rex/wait/$', 'exchtran.et.views.rexWait'),
	(r'^rex/reconcile/$', 'exchtran.et.views.rexReconcile'),
	(r'^rex/CheckAllOffered/$', 'exchtran.et.views.rexCheckAllOffered'),
	(r'^rex/component/submit/$', 'exchtran.et.views.rexComponentSubmit'),
	
	# API
	(r'^api/sessionStatus/$', 'exchtran.et.api.sessionStatus'),
	(r'^api/rex_toolTipImages/$', 'exchtran.et.api.rex_toolTipImages'),
	(r'^api/updateField/$', 'exchtran.et.api.updateField'),
	(r'^api/saveComponentChanges/$', 'exchtran.et.api.saveComponentChanges'),
	
	# Media Files
	(r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/Users/jonlesser/Documents/Berkeley/07Spring/ExchTrans/svn/exchtran/media'}),
	
	# Admin pages
	(r'^admin/', include('django.contrib.admin.urls')),
)
