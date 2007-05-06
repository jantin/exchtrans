from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import Context, Template, RequestContext
from django.core.exceptions import ObjectDoesNotExist
from et.models import *
from et.common import *
from et.textPage import *
import pickle
from time import time
from time import sleep

def profile_redirect(request):
	"""The generic login view directs to a profile page. This redirects accounts/profile to somewhere else"""
	return HttpResponseRedirect('/sessions')

@login_required
def sessions(request):
	"""This page shows the 'Waiting for participants' and 'In progress' experiments."""
	expSessions = ExperimentSession.objects.all()
	experiments = Experiment.objects.all()
	return render_to_response('adminInterface/sessions.html', 
							  {'expSessions': expSessions,
							'experiments': experiments}, 
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
	
	if(len(participants) > 0):
		noParticipants = False
	else:
		noParticipants = True
	

	return render_to_response('adminInterface/monitor.html', 
							  {'expSessions': expSessions, 
							   'monitorSession':monitorSession,
							   'participants':participants,
							   'noParticipants':noParticipants,
							   'running':running},
							  context_instance=RequestContext(request))
	

@login_required
def components(request):
	"""This page lists all components in the system."""
	components = Component.objects.all()
	componentTypes = ComponentTypes.objects.all()
	return render_to_response('adminInterface/components.html', 
							  {	'components': components, 
								'componentTypes': componentTypes}, 
							  context_instance=RequestContext(request))

@login_required
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

@login_required
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
											"The experimenter gave you 25 points to offer this round. Select a player below to make an offer to that player",
											"Participants Label", 
											"Make offer to: ",
											"Amount Label", 
											"Offer amount: ",
											"Submit Label", 
											"Submit Offer",
											"Waiting Text", 
											"Waiting for other players...",
											"Accept Text", 
											"Listed below are offers you received.",
											"Accept Button Label", 
											"Accept")
	
	
	if (componentType.componentType == "Questionnaire"):
		componentParams = {}
	
	if (componentType.componentType == "Text Page"):
		componentParams = textPageObj(	"",
										"",
										"",
										""
									)
	
	# Add component to the database
	c = Component(	name = componentName,
					parameters = pickle.dumps(componentParams),
					componentType = componentType
					)
	c.save()
	
	return HttpResponseRedirect('/components/edit/?id=' + str(c.id))

@login_required
def componentDelete(request):
	# TODO Don't delete, add a field to the model for inactive or something like that.
	"""This creates a new experiment session"""
	cid = request.GET.get('cid')
	comp = Component.objects.get(id=cid)
	comp.delete()
	
	return HttpResponseRedirect('/components')


@login_required
def editor(request):
	"""The editor allow you to create new experiments and edit existing ones."""
	experimentList = Experiment.objects.values('name', 'id')
	
	return render_to_response('adminInterface/editor.html', 
							  { 'experimentList': experimentList }, 
							  context_instance=RequestContext(request))

@login_required
def edit(request):
	"""This view allows you to edit an existing experiment"""
	expID = request.GET.get('id')
	expDetails = Experiment.objects.get(id=expID)
	componentList = Component.objects.all()
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
	return render_to_response('adminInterface/experiments.html', 
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
	
@login_required
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

@login_required
def removeComponent(request):
	# TODO convert this to a POST operation
	"""This removes a component from an experiment"""
	if (request.GET.get('removeComponentID') != ""):
		
		expID = request.GET.get('expID')
		expCompID = request.GET.get('expCompID');
			
		# insert the new component into the database
		ec = ExperimentComponents.objects.get(id=expCompID)
		ec.delete()
	
		# redirect back to the experiment editing page
	return HttpResponseRedirect('/experiments/edit/?id=' + expID)

@login_required
def newExperiment(request):
	"""This creates a new experiment"""
	if (request.POST.get('experimentName') != ""):

		# insert the new component into the database
		e = Experiment	(	name = request.POST.get('experimentName'),
					   		description = request.POST.get('experimentDescription'),
							status = experimentStatus.objects.get(statusText='Waiting for participants'),
							minPlayers = 4,
							maxPlayers = 4
						)
		e.save()
		
		# redirect back to the experiment editing page

	return HttpResponseRedirect('/experiments/edit/?id=' + str(e.id))

@login_required
def experimentDelete(request):
	# TODO Don't delete, add a field to the model for inactive or something like that.
	"""This creates a new experiment session"""
	eid = request.GET.get('eid')
	e = Experiment.objects.get(id=eid)
	e.delete()
	
	return HttpResponseRedirect('/experiments')

@login_required
def newSession(request):
	"""This creates a new experiment session"""
	expID = request.GET.get('id')
	expObject = Experiment.objects.get(id=expID)
	expSesStat = experimentSessionStatus.objects.get(statusText="Not Ready")
	e = ExperimentSession(experiment_id=expObject, status=expSesStat)
	e.save()
	sid = e.id
	
	return HttpResponseRedirect('/sessions/monitor/?sid=' + str(sid))

@login_required
def deleteSession(request):
	# TODO Don't delete, add a field to the model for inactive or something like that.
	"""This creates a new experiment session"""
	sid = request.GET.get('sid')
	expSes = ExperimentSession.objects.get(id=sid)
	expSes.delete()
	
	return HttpResponseRedirect('/sessions')


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
	p.name = p.dateCreated.strftime("%Y-%m-%d") + "_" + str(p.id).rjust(6,"0")
	p.save()
	
	if(expSes.status.statusText == "Not Ready"):
		expSes.status = experimentSessionStatus.objects.get(statusText="Ready")
		expSes.save()
	
	return HttpResponseRedirect('/session/wait/?pname=' + p.name + '&sid=' + sid)
	
@login_required
def wait(request):
	"""Put the participant at a waiting screen."""
	return render_to_response('session/waiting.html', 
						  {'waitReason': "Waiting for experimenter to start...",
						   'partName': request.GET.get('pname'),
						   'sid': request.GET.get('sid')}, 
						  context_instance=RequestContext(request))

@login_required
def rexOffer(request):
	"""Asks the participant to make an offer to other participants"""
	sid = request.GET.get('sid')
	pname = request.GET.get('pname')
	
	p = Participant.objects.get(name=pname)
	cumulativePoints = p.cumulativePoints
	sesVars = loadSessionVars(sid)
	parameters = pickle.loads(sesVars.componentsList[int(p.currentComponent)].component_id.parameters)
	otherParticipants = Participant.objects.filter(experimentSession=sid).exclude(name=pname)
	
	
	return render_to_response('rex/rex_offer.html', 
							{	'sid': sid, 
								'pname': pname,
								'parameters': parameters,
								'otherParticipants': otherParticipants,
								'cumulativePoints': cumulativePoints
							}, 
						  	context_instance=RequestContext(request))
	
@login_required
def rexOfferSubmit(request):
	"""Validates the particpant's offer and passes them on to the waiting screen"""
	sid = request.GET.get('sid')
	pname = request.GET.get('pname')
	sessionObj = ExperimentSession.objects.get(id=sid)
	p = Participant.objects.get(name=pname)
	cumulativePoints = p.cumulativePoints
	
	sesVars = loadSessionVars(sid)
	parameters = pickle.loads(sesVars.componentsList[int(p.currentComponent)].component_id.parameters)
	
	toParticipant = request.POST.get('toParticipant')
	fromParticipant = pname
	offerAmount = request.POST.get('offerAmount')
	
	offerObj = offer(toParticipant,fromParticipant,offerAmount)
	
	sesVarKey = "offer_" + str(p.currentComponent) + "_" + str(p.currentIteration)
	sv = SessionVar(experimentSession=sessionObj, key=sesVarKey, value=pickle.dumps(offerObj))
	sv.save()
	
	return render_to_response('rex/rex_wait.html', 
						  	{	'sid': sid, 
								'pname': pname, 
								'parameters': parameters,
								'cumulativePoints': cumulativePoints
							}, 
						  context_instance=RequestContext(request))

@login_required
def rexCheckAllOffered(request):
	"""Checks to see if all the participants have made an offer"""
	sid = request.GET.get('sid')
	pname = request.GET.get('pname')
	sessionObj = ExperimentSession.objects.get(id=sid)
	
	p = Participant.objects.get(name=pname)
	sesVarKey = "offer_" + str(p.currentComponent) + "_" + str(p.currentIteration)

	offers = SessionVar.objects.filter(experimentSession=sessionObj, key=sesVarKey)
	participantsList = Participant.objects.filter(experimentSession__exact=sid)
	
	if(len(participantsList) == len(offers)):
		response = "Ready"
	else:
		response = "Not Ready"
	
	if(sessionObj.status.statusText == "Canceled"):
		response = "Canceled"
	
	return render_to_response('api.html', 
						  {'response': response}, 
						  context_instance=RequestContext(request))

@login_required
def rexReconcile(request):
	"""Sorts through all the offers made to figure out who receives what."""
	sid = request.GET.get('sid')
	pname = request.GET.get('pname')
	sessionObj = ExperimentSession.objects.get(id=sid)
	sesVars = loadSessionVars(sid)
	p = Participant.objects.get(name=pname)
	
	parameters = pickle.loads(sesVars.componentsList[int(p.currentComponent)].component_id.parameters)
	
	sesVarKey = "offer_" + str(p.currentComponent) + "_" + str(p.currentIteration)
	offers = SessionVar.objects.filter(experimentSession=sessionObj, key=sesVarKey)
	
	myOffers = []
	for o in offers:
		offerObj = pickle.loads(o.value)
		if (offerObj.toParticipant == pname):
			myOffer = {}
			myOffer['from'] = offerObj.fromParticipant
			myOffer['amount'] = offerObj.amount
			myOffers.append(myOffer)
			p.cumulativePoints = p.cumulativePoints + long(offerObj.amount)
			p.save()
		
		cumulativePoints = p.cumulativePoints
	
	return render_to_response('rex/rex_accept.html', 
							{	'sid': sid, 
								'pname': pname,
								'parameters': parameters,
								'myOffers': myOffers,
								'cumulativePoints': cumulativePoints
							}, 
						  	context_instance=RequestContext(request))

@login_required
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


@login_required
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
	# TODO Don't need current component and current iteration in sessionVaiables object
	sesVars = sessionVariables(componentsList, 0, 0, participantsList)
	sv = SessionVar(experimentSession=sessionObj, key="sesVars", value=pickle.dumps(sesVars))
	sv.save()
	
	if(sessionObj.status.statusText != "Not Ready"):
		# Change status to Running
		sesStatus = experimentSessionStatus.objects.get(statusText="Running")
		sessionObj.status = sesStatus
		sessionObj.save()
	
	return HttpResponseRedirect('/sessions/monitor/?sid=' + sid)

@login_required
def stopSession(request):
	"""Stops the session"""
	sid = request.GET.get('sid')
	expSes = ExperimentSession.objects.get(id=sid)
	
	# Delete sesVars
	SessionVar.objects.filter(experimentSession=expSes).delete()
	
	# Delete participants
	Participant.objects.filter(experimentSession__exact=sid).delete()
	
	if(expSes.status.statusText == "Running"):
		# Change status from Running to canceled
		sesStatus = experimentSessionStatus.objects.get(statusText="Canceled")
		expSes.status = sesStatus
		expSes.save()
	
	return HttpResponseRedirect('/sessions/monitor/?sid=' + sid)

@login_required
def endSession(request):
	"""This function handles what happens when the experiment is over."""

	# TODO delete participant, if last participant, kill sesVars, add end date to session.
	return render_to_response('session/end.html', 
						  {'response': "Experiment finished"}, 
						  context_instance=RequestContext(request))

@login_required
def bootParticipant(request):
	# TODO Don't delete, add a field to the model for inactive or something like that.
	"""Boots participants by deleting them"""
	sid = request.GET.get('sid')
	pid = request.GET.get('pid')
	p = Participant.objects.get(id=pid)
	p.delete()
	
	return HttpResponseRedirect('/sessions/monitor/?sid=' + sid)

@login_required
def booted(request):
	"""Moves booted participants to a booted screen"""
	
	return render_to_response('session/booted.html', 
						  {'response': "booted"}, 
						  context_instance=RequestContext(request))
	

@login_required
def driveSession(request):
	"""Moves participants along the session"""
	print "\n----\n 1 \n----\n"
	pname = request.GET.get('pname')
	sid = request.GET.get('sid')
	expSes = ExperimentSession.objects.get(id=sid)
	sesVars = loadSessionVars(sid)
	print "\n----\n 2 \n----\n"
	# Quick check to make sure the session is still running.
	if(expSes.status.statusText != "Running"):
		return HttpResponseRedirect('/session/wait/?pname=' + pname + '&sid=' + sid)
	
	# Get the participant object
	try:
		p = Participant.objects.get(name=pname)
	except ObjectDoesNotExist:
		# TODO kill the session here in this case
		return HttpResponseRedirect("/session/booted/")
	print "\n----\n 3 \n----\n"
	'''
	print "\n---------------\n\n"
	print "p.currentComponent: "
	print p.currentComponent
	
	print "len(sesVars.componentsList): "
	print len(sesVars.componentsList)
	
	print "p.currentIteration: "
	print p.currentIteration
	
	print "\n---------------\n\n"
	
	print "sesVars.componentsList[p.currentComponent].iterations: "
	print sesVars.componentsList[int(p.currentComponent)].iterations
	'''
	
	
	if(sesVars.componentsList[int(p.currentComponent)].iterations == p.currentIteration):
		p.currentComponent = p.currentComponent + 1
		p.currentIteration = 0

		if(len(sesVars.componentsList) == p.currentComponent):
			return HttpResponseRedirect('/session/end/?sid=' + sid)
	print "\n----\n 4 \n----\n"
	p.currentIteration = p.currentIteration + 1
	p.save()
	print "\n----\n 5 \n----\n"
	componentFunctionName = sesVars.componentsList[int(p.currentComponent)].component_id.componentType.kickoffFunction
	
	try:
		resp = HttpResponseRedirect('/' + componentFunctionName + '/?pname=' + pname + '&sid=' + sid)
	except IOError, (errno, strerror):
		print "OMG! I/O error(%s): %s" % (errno, strerror)
	print "\n----\n 6 \n----\n"
	return resp

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

@login_required
def scratch(request):
	"""outputs scratch template for UI dev"""
	return render_to_response('scratch.html', 
						  {'name': "value"}, 
						  context_instance=RequestContext(request))