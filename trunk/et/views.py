from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import Context, Template, RequestContext
from et.models import *
import pickle
from time import time

def profile_redirect(request):
	"""The generic login view directs to a profile page. This redirects accounts/profile to somewhere else"""
	return HttpResponseRedirect('/dashboard')

@login_required
def dashboard(request):
	"""This page shows the 'Waiting for participants' and 'In progress' experiments."""
	expSessions = ExperimentSession.objects.all()
	return render_to_response('adminInterface/dashboard.html', 
							  {'expSessions': expSessions}, 
							  context_instance=RequestContext(request))

@login_required
def monitor(request):
	"""This page allows the experimenter to monitor the progress of a running experiment."""
	# fetch all sessions for sessions drop down
	expSessions = ExperimentSession.objects.all()
	
	
	sid = request.GET.get('sid')
	monitorSession = ExperimentSession.objects.get(id=sid)
	participants = Participant.objects.filter(experimentSession__exact=sid)
	
	if(monitorSession.status.statusText == "Running"):
		running = True
	else:
		running = False
	
	return render_to_response('adminInterface/monitor.html', 
							  {'expSessions': expSessions, 
							   'monitorSession':monitorSession,
							   'participants':participants,
							   'running':running},
							  context_instance=RequestContext(request))
	


def components(request):
	"""This page lists all components in the system."""
	components = Component.objects.all()
	componentTypes = ComponentTypes.objects.all()
	return render_to_response('adminInterface/components.html', 
							  {	'components': components, 
								'componentTypes': componentTypes}, 
							  context_instance=RequestContext(request))


def componentEdit(request):
	"""This page displays a single component for editing"""
	comID = request.GET.get('id')
	component = Component.objects.get(id=comID)
	parameters = pickle.loads(component.parameters)
	
	return render_to_response(	component.componentType.editTemplate, 
								{'component': component,
								 'parameters': parameters}, 
						  		context_instance=RequestContext(request))


# TODO delete component
# TODO duplicate component
# TODO export component
# TODO load component


def componentCreate(request):
	"""This function creates a new component instance"""
	# Get information from POST vars
	componentName = request.POST.get('componentName')
	componentType = request.POST.get('componentType')
	
	# Get component type object
	componentType = ComponentTypes.objects.get(id=componentType)
	
	# Set default parameters
	# TODO Add better defaults
	if (componentType.componentType == "Reciprocal Exchange"):
		componentParams = rexParameters(	"Available Points",
											"25",
											"Prompt Text", 
											"Prompt Text Value",
											"Participants Label", 
											"Participants Label Value",
											"Amount Label", 
											"Amount Label Value",
											"Submit Label", 
											"Submit Label Value",
											"Waiting Text", 
											"Waiting Text Value",
											"Accept Text", 
											"Accept Text Value",
											"Accept Button Label", 
											"Accept Button Label Value")
	
	
	if (componentType.componentType == "Questionnaire"):
		componentParams = {}
	
	
	# Add component to the database
	c = Component(	name = componentName,
					parameters = pickle.dumps(componentParams),
					componentType = componentType
					)
	c.save()
	
	return HttpResponseRedirect('/components/edit/?id=' + str(c.id))



@login_required
def editor(request):
	"""The editor allow you to create new experiments and edit existing ones."""
	experimentList = Experiment.objects.values('name', 'id')
	
	return render_to_response('adminInterface/editor.html', 
							  { 'experimentList': experimentList }, 
							  context_instance=RequestContext(request))

def edit(request):
	"""This view allows you to edit an existing experiment"""
	expID = request.GET.get('id')
	expDetails = Experiment.objects.get(id=expID)
	componentList = Component.objects.values()
	experimentComponentsList = ExperimentComponents.objects.filter(experiment_id__exact=expID)	

	return render_to_response('adminInterface/edit.html', 
							  { 'expID': expID, 
								'componentList': componentList, 
								'experimentComponentsList': experimentComponentsList,
								'expDetails': expDetails }, 
							  context_instance=RequestContext(request))

@login_required
def experiments(request):
	"""This page lists all experiments in the system."""
	experiments = Experiment.objects.all()
	return render_to_response('adminInterface/archive.html', 
							  {'experiments': experiments}, 
							  context_instance=RequestContext(request))


@login_required
def viewExperiment(request):
	"""This page lists all experiments in the system."""
	expID = request.GET.get('id')
	experimentComponentsList = ExperimentComponents.objects.filter(experiment_id__exact=expID)
	experimentSessions = ExperimentSession.objects.filter(experiment_id__exact=expID)
	experiment = Experiment.objects.get(id=expID)
	return render_to_response('adminInterface/experimentView.html', 
							  {'experiment': experiment,
							   'experimentComponentsList': experimentComponentsList,
							   'experimentSessions': experimentSessions
							   }, 
							  context_instance=RequestContext(request))
	

def addComponent(request):
	"""This adds a component to an experiment"""
	if (request.POST.get('addComponentID') != ""):
		# put the new component in last place
		orderCount = ExperimentComponents.objects.filter(experiment_id__exact=request.POST.get('expID')).count() + 1
	
		# insert the new component into the database
		ec = ExperimentComponents(experiment_id=Experiment.objects.get(id=request.POST.get('expID')),
								   component_id=Component.objects.get(id=request.POST.get('addComponentID')),
								iterations=1,
									order=orderCount)
		ec.save()
	
		# redirect back to the experiment editing page
	
	return HttpResponseRedirect('/experiments/edit/?id=' + request.POST.get('expID'))

def newExperiment(request):
	"""This creates a new experiment"""
	if (request.POST.get('experimentName') != ""):

		# insert the new component into the database
		e = Experiment(name=request.POST.get('experimentName'),
					   description=request.POST.get('experimentDescription'),
						status=experimentStatus.objects.get(statusText='active'))
		e.save()
		
		# redirect back to the experiment editing page

	return HttpResponseRedirect('/experiments/edit/?id=' + str(e.id))

def newSession(request):
	"""This creates a new experiment session"""
	expID = request.GET.get('id')
	expObject = Experiment.objects.get(id=expID)
	expSesStat = experimentSessionStatus.objects.get(statusText="Not Ready")
	e = ExperimentSession(experiment_id=expObject, status=expSesStat)
	e.save()
	
	return HttpResponseRedirect('/experiments/view/?id=' + expID)

def deleteSession(request):
	"""This creates a new experiment session"""
	sid = request.GET.get('sid')
	expObject = Experiment.objects.get(id=expID)
	expSesStat = experimentSessionStatus.objects.get(statusText="Not Ready")
	e = ExperimentSession(experiment_id=expObject, status=expSesStat)
	e.save()
	
	return HttpResponseRedirect('/experiments/view/?id=' + str(expID))


@login_required
def joinSession(request):
	"""Creates a participant object and add it to the session."""
	sid = request.GET.get('sid')
	
	# Set participant's status
	partiStatus = participantStatus.objects.get(statusText="Ready")
	expSes = ExperimentSession.objects.get(id=sid)
	p = Participant(status=partiStatus, experimentSession=expSes, currentIteration=0, currentComponent=0)
	p.save()
	
	# Set participant's name
	p.name = p.dateCreated.strftime("%Y-%m-%d") + "_" + str(p.id).rjust(4,"0")
	p.save()
	
	if(expSes.status.statusText == "Not Ready"):
		expSes.status = experimentSessionStatus.objects.get(statusText="Ready")
		expSes.save()
	
	return HttpResponseRedirect('/session/wait/?pname=' + p.name + '&sid=' + sid)
	

def wait(request):
	"""Put the participant at a waiting screen."""
	return render_to_response('session/waiting.html', 
						  {'waitReason': "Waiting for experimenter to start...",
						   'partName': request.GET.get('pname'),
						   'sid': request.GET.get('sid')}, 
						  context_instance=RequestContext(request))


def rexInit(request):
	"""Asks the participant to make an offer to other participants"""
	
	return render_to_response('rex/rex_offer.html', 
						  {'waitReason': "Waiting for experimenter to start"}, 
						  context_instance=RequestContext(request))


def rexOffer(request):
	"""Asks the participant to make an offer to other participants"""
	sid = request.GET.get('sid')
	pname = request.GET.get('pname')
	
	return render_to_response('rex/rex_offer.html', 
						  {'sid': sid, 'pname': pname}, 
						  context_instance=RequestContext(request))
	

def rexOfferSubmit(request):
	"""Validates the particpant's offer and passes them on to the waiting screen"""
	sid = request.GET.get('sid')
	pname = request.GET.get('pname')
	sessionObj = ExperimentSession.objects.get(id=sid)
	offerList = []
	
	toParticipant = request.POST.get('toParticipant')
	fromParticipant = pname
	offerAmount = request.POST.get('offerAmount')
	
	offerObj = offer(toParticipant,fromParticipant,offerAmount)
	
	sv = SessionVar(experimentSession=sessionObj, key="offers", value=pickle.dumps(offerObj))
	sv.save()
	
	return render_to_response('rex/rex_wait.html', 
						  {'sid': sid, 'pname': pname, 'waitReason':"Waiting for other players..."}, 
						  context_instance=RequestContext(request))


def rexCheckAllOffered(request):
	"""Checks to see if all the participants have made an offer"""
	sid = request.GET.get('sid')
	pname = request.GET.get('pname')
	sessionObj = ExperimentSession.objects.get(id=sid)
	
	offers = SessionVar.objects.filter(experimentSession=sessionObj, key="offers")
	participantsList = Participant.objects.filter(experimentSession__exact=sid)
	
	if(len(participantsList) == len(offers)):
		response = "Ready"
	else:
		response = "Not Ready"
	
	
	return render_to_response('api.html', 
						  {'response': response}, 
						  context_instance=RequestContext(request))

def rexReconcile(request):
	"""Asks the participant to make an offer to other participants"""
	sid = request.GET.get('sid')
	pname = request.GET.get('pname')
	sessionObj = ExperimentSession.objects.get(id=sid)
	offers = SessionVar.objects.filter(experimentSession=sessionObj, key="offers")
	offers.delete()
	
	
	return render_to_response('rex/rex_accept.html', 
						  {'sid': sid, 'pname': pname}, 
						  context_instance=RequestContext(request))


def rexComponentSubmit(request):
	"""Accepts the rex component form and updates the database"""
	
	comID = request.POST.get("comIM")
	
	componentParams = rexParameters(	"Available Points",
										request.POST.get("Available Points"),
										"Prompt Text", 
										request.POST.get("Prompt Text"),
										"Participants Label", 
										request.POST.get("Participants Label"),
										"Amount Label", 
										request.POST.get("Amount Label"),
										"Submit Label", 
										request.POST.get("Submit Label"),
										"Waiting Text", 
										request.POST.get("Waiting Text"),
										"Accept Text", 
										request.POST.get("Accept Text"),
										"Accept Button Label", 
										request.POST.get("Accept Button Label")
									)

	c = Component.objects.get(id=comID)
	c.name = request.POST.get("componentName")
	c.description = request.POST.get("componentDescription")
	c.parameters = pickle.dumps(componentParams)
	
	c.save()
	
	response = "Component Saved"
	return render_to_response('api.html', 
						  {'response': response}, 
						  context_instance=RequestContext(request))



def startSession(request):
	"""Initiates the experiment session"""	

	sid = request.GET.get('sid')
	
	# Get the session object
	sessionObj = ExperimentSession.objects.get(id=sid)
	
	# Get a list of the components
	componentsList = ExperimentComponents.objects.filter(experiment_id__exact=sessionObj.experiment_id.id)

	# Get a list of the participants
	participantsList = Participant.objects.filter(experimentSession__exact=sid)
	
	# Clean out the SessionVar table rows
	SessionVar.objects.filter(experimentSession=sessionObj).delete()
	
	# Make a sessionVariables object, pickle it, store it in SessionVar table
	sesVars = sessionVariables(componentsList, 0, 0, participantsList)
	sv = SessionVar(experimentSession=sessionObj, key="sesVars", value=pickle.dumps(sesVars))
	sv.save()
	
	if(sessionObj.status.statusText == "Ready"):
		# Change status to Running
		sesStatus = experimentSessionStatus.objects.get(statusText="Running")
		sessionObj.status = sesStatus
		sessionObj.save()
	
	return HttpResponseRedirect('/dashboard/monitor/?sid=' + sid)

def stopSession(request):
	"""Stops the session"""
	sid = request.GET.get('sid')
	expSes = ExperimentSession.objects.get(id=sid)
	
	if(expSes.status.statusText == "Running"):
		# Change status to Running
		sesStatus = experimentSessionStatus.objects.get(statusText="Ready")
		expSes.status = sesStatus
		expSes.save()
	
	return HttpResponseRedirect('/dashboard/monitor/?sid=' + sid)


def driveSession(request):
	"""Moves participants along the session"""
	pname = request.GET.get('pname')
	sid = request.GET.get('sid')
	expSes = ExperimentSession.objects.get(id=sid)
	
	# Quick check to make sure the session is still running.
	if(expSes.status.statusText != "Running"):
		return HttpResponseRedirect('/session/wait/?pname=' + pname + '&sid=' + sid)
	
	# Get the participant object and load session variables
	p = Participant.objects.get(name=pname)
	sv = SessionVar.objects.get(experimentSession=expSes,key="sesVars")
	sesVars = pickle.loads(sv.value)
	
	
	if(sesVars.componentsList[p.currentComponent].iterations == p.currentIteration):
		p.currentComponent = p.currentComponent + 1
		p.currentIteration = 0
		if(len(sesVars.componentsList) == p.currentComponent):
			return HttpResponseRedirect('/session/end')
	
	p.currentIteration = p.currentIteration + 1
	p.save()
	
	componentFunctionName = sesVars.componentsList[sesVars.currentComponent].component_id.functionName
	return HttpResponseRedirect('/' + componentFunctionName + '/?pname=' + pname + '&sid=' + sid)



class rex:
	"""This class drives reciprocal exchange"""
	def __init__(self, participants, params):
		self.participants = participants
		self.params = params
	
class sessionVariables:
	"""A data structure for session variables (not http sessions)"""	
	def __init__(self, componentsList, currentComponent, currentIteration, participantsList):
		self.componentsList = componentsList
		self.currentComponent = currentComponent
		self.currentIteration = currentIteration
		self.participantsList = participantsList

class offer(object):
	"""A Data structure for holding participant offers"""
	def __init__(self, toParticipant, fromParticipant, amount):
		self.fromParticipant = fromParticipant
		self.toParticipant = toParticipant
		self.amount = amount
		self.timestamp = time()


class rexParameters(object):
	"""A Data structure for holding parameters"""
	def __init__(self, 	AvailablePoints,
						AvailablePointsValue,
						PromptText,
						PromptTextValue,
						ParticipantsLabel,
						ParticipantsLabelValue,
						AmountLabel,
						AmountLabelValue,
						SubmitLabel,
						SubmitLabelValue,
						WaitingText,
						WaitingTextValue,
						AcceptText,
						AcceptTextValue,
						AcceptButtonLabel,
						AcceptButtonLabelValue):
		self.AvailablePoints = AvailablePoints
		self.AvailablePointsValue = AvailablePointsValue
		self.PromptText = PromptText
		self.PromptTextValue = PromptTextValue
		self.ParticipantsLabel = ParticipantsLabel
		self.ParticipantsLabelValue = ParticipantsLabelValue
		self.AmountLabel = AmountLabel
		self.AmountLabelValue = AmountLabelValue
		self.SubmitLabel = SubmitLabel
		self.SubmitLabelValue = SubmitLabelValue
		self.WaitingText = WaitingText
		self.WaitingTextValue = WaitingTextValue
		self.AcceptText = AcceptText
		self.AcceptTextValue = AcceptTextValue
		self.AcceptButtonLabel = AcceptButtonLabel
		self.AcceptButtonLabelValue = AcceptButtonLabelValue


def scratch(request):
	"""outputs scratch template for UI dev"""
	return render_to_response('scratch.html', 
						  {'name': "value"}, 
						  context_instance=RequestContext(request))