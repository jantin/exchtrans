from django.conf.urls.defaults import *
from django.contrib.auth.views import *
from exchtran.et.views import *

urlpatterns = patterns('',
	# ET Admin Pages
	(r'^$', 'exchtran.et.session.sessions'),
	
	# Monitoring
	(r'^sessions/monitor/$', 'exchtran.et.monitor.monitor'),
	(r'^sessions/monitor/updatePollProcess/$', 'exchtran.et.monitor.updatePollProcess'),
	(r'^sessions/monitor/bootParticipant/$', 'exchtran.et.monitor.bootParticipant'),

	# Experiments
	(r'^experiments/$', 'exchtran.et.experiment.experiments'),
	(r'^experiments/view/$', 'exchtran.et.experiment.viewExperiment'),				
	(r'^experiments/edit/$', 'exchtran.et.experiment.edit'),
	(r'^experiments/edit/addComponent/$', 'exchtran.et.experiment.addComponent'),
	(r'^experiments/edit/removeComponent/$', 'exchtran.et.experiment.removeComponent'),
	(r'^experiments/edit/newExperiment/$', 'exchtran.et.experiment.newExperiment'),	
	(r'^experiments/delete/$', 'exchtran.et.experiment.experimentDelete'),
	(r'^experiments/newSession/$', 'exchtran.et.session.newSession'),
	
	# Components
	(r'^components/$', 'exchtran.et.component.components'),
	(r'^components/create/$', 'exchtran.et.component.componentCreate'),
	(r'^components/edit/$', 'exchtran.et.component.componentEdit'),
	(r'^components/delete/$', 'exchtran.et.component.componentDelete'),
	
	# Misc utility pages
	(r'^scratch/$', 'exchtran.et.views.scratch'),
	(r'^httpRPS/$', 'exchtran.et.views.httpRPS'),
	
	# ET Experiment Session Pages
	(r'^sessions/$', 'exchtran.et.session.sessions'),
	(r'^session/join/$', 'exchtran.et.session.joinSession'),
	(r'^session/wait/$', 'exchtran.et.session.wait'),
	(r'^session/start/$', 'exchtran.et.session.startSession'),
	(r'^session/stop/$', 'exchtran.et.session.stopSession'),	
	(r'^session/drive/$', 'exchtran.et.session.driveSession'),
	(r'^session/delete/$', 'exchtran.et.session.deleteSession'),
	(r'^session/end/$', 'exchtran.et.session.endSession'),
	(r'^session/booted/$', 'exchtran.et.session.booted'),
			
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
	(r'^nex/incomingOfferDeclinedToView/$', 'exchtran.et.nex.incomingOfferDeclinedToView'),
	(r'^nex/confirmCancel/$', 'exchtran.et.nex.confirmCancel'),
	(r'^nex/incomingOffer/$', 'exchtran.et.nex.incomingOffer'),
	(r'^nex/confirmEndRound/$', 'exchtran.et.nex.confirmEndRound'),
	(r'^nex/nonBindingConfirmation/$', 'exchtran.et.nex.nonBindingConfirmation'),
	(r'^nex/nonBindingPollProcess/$', 'exchtran.et.nex.nonBindingPollProcess'),	
	(r'^nex/transactionSummary/$', 'exchtran.et.nex.transactionSummary'),
	(r'^nex/nextRoundCountdownPollProcess/$', 'exchtran.et.nex.nextRoundCountdownPollProcess'),	
	(r'^nex/nextRoundCountdown/$', 'exchtran.et.nex.nextRoundCountdown'),
	(r'^nex/getPollURL/$', 'exchtran.et.nex.getPollURL'),
	(r'^nex/timerRanOut/$', 'exchtran.et.nex.timerRanOut'), # n8 added to deal with time running out
			
	# Matcher
	(r'^matcher/display/$', 'exchtran.et.matcher.matcherDisplay'),
	(r'^matcher/submit/$', 'exchtran.et.matcher.matcherEdit'),
	(r'^matcher/deciderSubmit/$', 'exchtran.et.matcher.deciderSubmit'),
	(r'^matcher/checkDecision/$', 'exchtran.et.matcher.checkDeciderChoice'),
	(r'^matcher/followDecider/$', 'exchtran.et.matcher.followDecider'),
	
	# Questionnaire
	(r'^questionnaire/display/$', 'exchtran.et.questionnaire.questionnaireDisplay'),
	(r'^questionnaire/participantSubmit/$', 'exchtran.et.questionnaire.participantSubmit'),
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
	(r'^rex/component/submit/$', 'exchtran.et.rex.rexEdit'),
	(r'^rex/display/$', 'exchtran.et.rex.rexDisplay'),
	(r'^rex/checkForOpponentPollProcess/$', 'exchtran.et.rex.checkForOpponentPollProcess'),
	(r'^rex/makeOfferButton/$', 'exchtran.et.rex.makeOfferButton'),
	(r'^rex/offerFormulation/$', 'exchtran.et.rex.offerFormulation'),
	(r'^rex/waitingScreenPollProcess/$', 'exchtran.et.rex.waitingScreenPollProcess'),	
	(r'^rex/transactionSummary/$', 'exchtran.et.rex.transactionSummary'),
	(r'^rex/nextRoundCountdownPollProcess/$', 'exchtran.et.rex.nextRoundCountdownPollProcess'),	
	(r'^rex/nextRoundCountdown/$', 'exchtran.et.rex.nextRoundCountdown'),
		
	# API
	(r'^api/sessionStatus/$', 'exchtran.et.api.sessionStatus'),
	(r'^api/rex_toolTipImages/$', 'exchtran.et.api.rex_toolTipImages'),
	(r'^api/updateField/$', 'exchtran.et.api.updateField'),
	(r'^api/saveComponentChanges/$', 'exchtran.et.api.saveComponentChanges'),
	
	# Media Files
  (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/Users/n8agrin/Sites/exchtran/media'}),
  # (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/home/exchtrans/django_projects/exchtran/media'}),
	
	# Admin pages
	(r'^admin/', include('django.contrib.admin.urls')),
)
