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
	
	# Questionnaire
	(r'^questionnaire/display/$', 'exchtran.et.questionnaire.questionnaireDisplay'),
	(r'^questionnaire/editParam/$', 'exchtran.et.questionnaire.questionnaireEditParam'),
	(r'^questionnaire/addQuestion/$', 'exchtran.et.questionnaire.questionnaireAddQ'),
	(r'^questionnaire/deleteQuestion/$', 'exchtran.et.questionnaire.questionnaireDeleteQ'),
	(r'^questionnaire/addRadioChoice/$', 'exchtran.et.questionnaire.addRadioChoice'),
	(r'^questionnaire/deleteRadioChoice/$', 'exchtran.et.questionnaire.deleteRadioChoice'),
	(r'^questionnaire/editRadioChoice/$', 'exchtran.et.questionnaire.editRadioChoice'),
	(r'^questionnaire/backCheckbox/$', 'exchtran.et.questionnaire.handleBackCheckbox'),	
	
	# Rex: Reciprocal Exchange
	(r'^rexOffer/$', 'exchtran.et.rex.rexOffer'),
	(r'^rexOffer/submit/$', 'exchtran.et.rex.rexOfferSubmit'),
	(r'^rex/wait/$', 'exchtran.et.rex.rexWait'),
	(r'^rex/reconcile/$', 'exchtran.et.rex.rexReconcile'),
	(r'^rex/CheckAllOffered/$', 'exchtran.et.rex.rexCheckAllOffered'),
	(r'^rex/component/submit/$', 'exchtran.et.rex.rexComponentSubmit'),
	
	# API
	(r'^api/sessionStatus/$', 'exchtran.et.api.sessionStatus'),
	(r'^api/rex_toolTipImages/$', 'exchtran.et.api.rex_toolTipImages'),
	(r'^api/updateField/$', 'exchtran.et.api.updateField'),
	(r'^api/saveComponentChanges/$', 'exchtran.et.api.saveComponentChanges'),
	
	# Media Files
	(r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/opt/local/lib/python2.4/site-packages/exchtran/media'}),
	
	# Admin pages
	(r'^admin/', include('django.contrib.admin.urls')),
)
