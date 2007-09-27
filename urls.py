from django.conf.urls.defaults import *
from django.contrib.auth.views import *
from exchtran.et.views import *

urlpatterns = patterns('',
	# ET Admin Pages
	(r'^$', 'exchtran.et.views.sessions'),
	(r'^sessions/$', 'exchtran.et.views.sessions'),
	(r'^sessions/monitor/$', 'exchtran.et.monitor.monitor'),

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
	(r'^httpRPS/$', 'exchtran.et.views.httpRPS'),
	
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

	# Negotiated Exchange
	(r'^nex/submit/$', 'exchtran.et.nex.nexEdit'),
	(r'^nex/display/$', 'exchtran.et.nex.nexDisplay'),
	(r'^nex/checkForOpponentPollProcess/$', 'exchtran.et.nex.checkForOpponentPollProcess'),
	(r'^nex/checkForOfferPollProcess/$', 'exchtran.et.nex.checkForOfferPollProcess'),
	(r'^nex/makeOfferButton/$', 'exchtran.et.nex.makeOfferButton'),
	(r'^nex/offerFormulation/$', 'exchtran.et.nex.offerFormulation'),
	(r'^nex/checkForCancelWhileWaitingPollProcess/$', 'exchtran.et.nex.checkForCancelWhileWaitingPollProcess'),
	(r'^nex/counterOfferFormulation/$', 'exchtran.et.nex.counterOfferFormulation'),
	(r'^nex/waitingScreen/$', 'exchtran.et.nex.waitingScreen'),
	(r'^nex/waitingScreenPollProcess/$', 'exchtran.et.nex.waitingScreenPollProcess'),	
	(r'^nex/confirmCancel/$', 'exchtran.et.nex.confirmCancel'),
	(r'^nex/incomingOffer/$', 'exchtran.et.nex.incomingOffer'),
	(r'^nex/confirmEndRound/$', 'exchtran.et.nex.confirmEndRound'),
	(r'^nex/nonBindingConfirmation/$', 'exchtran.et.nex.nonBindingConfirmation'),
	(r'^nex/transactionSummary/$', 'exchtran.et.nex.transactionSummary'),
	(r'^nex/nextRoundCountdown/$', 'exchtran.et.nex.nextRoundCountdown'),
			
	# Matcher
	(r'^matcher/display/$', 'exchtran.et.matcher.matcherDisplay'),
	(r'^matcher/submit/$', 'exchtran.et.matcher.matcherEdit'),
	(r'^matcher/deciderSubmit/$', 'exchtran.et.matcher.deciderSubmit'),
	(r'^matcher/checkDecision/$', 'exchtran.et.matcher.checkDeciderChoice'),
	(r'^matcher/followDecider/$', 'exchtran.et.matcher.followDecider'),
	
	# Questionnaire
	(r'^questionnaire/display/$', 'exchtran.et.questionnaire.questionnaireDisplay'),
	(r'^questionnaire/editParam/$', 'exchtran.et.questionnaire.questionnaireEditParam'),
	(r'^questionnaire/addQuestion/$', 'exchtran.et.questionnaire.questionnaireAddQ'),
	(r'^questionnaire/deleteQuestion/$', 'exchtran.et.questionnaire.questionnaireDeleteQ'),
	(r'^questionnaire/addRadioChoice/$', 'exchtran.et.questionnaire.addRadioChoice'),
	(r'^questionnaire/deleteRadioChoice/$', 'exchtran.et.questionnaire.deleteRadioChoice'),
	(r'^questionnaire/editRadioChoice/$', 'exchtran.et.questionnaire.editRadioChoice'),
	(r'^questionnaire/backCheckbox/$', 'exchtran.et.questionnaire.handleBackCheckbox'),	
	
	# Widgets
	(r'^widgets/timer/display/$', 'exchtran.et.widgets.timerDisplay'),
	(r'^widgets/timer/editSubmit/$', 'exchtran.et.widgets.timerEdit'),
	(r'^widgets/image/display/$', 'exchtran.et.widgets.imageDisplay'),
	(r'^widgets/image/editSubmit/$', 'exchtran.et.widgets.imageEdit'),
	(r'^widgets/bank/display/$', 'exchtran.et.widgets.bankDisplay'),
	(r'^widgets/bank/editSubmit/$', 'exchtran.et.widgets.bankEdit'),
	
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
