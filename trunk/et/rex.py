from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import Context, Template, RequestContext
from django.core.exceptions import ObjectDoesNotExist
from models import *
from common import *
from textPage import *
from views import *
import pickle
from time import time
from time import sleep

class offer(object):
	"""A Data structure for holding participant offers"""
	def __init__(self, toParticipant, fromParticipant, amount):
		self.fromParticipant = fromParticipant
		self.toParticipant = toParticipant
		self.amount = amount
		self.timestamp = time()


class rexParameters(object):
	"""A Data structure for holding parameters"""
	def __init__(self, 	AvailablePoints = "Available Points",
						AvailablePointsValue = "50",
						PromptText = "Prompt Text",
						PromptTextValue = "The experimenter gave you 25 points to offer this round. Select a player below to make an offer to that player",
						ParticipantsLabel = "Participants Label",
						ParticipantsLabelValue = "Make offer to: ",
						AmountLabel = "Amount Label",
						AmountLabelValue = "Offer amount: ",
						SubmitLabel = "Submit Label",
						SubmitLabelValue = "Submit Offer",
						WaitingText = "Waiting Text",
						WaitingTextValue = "Waiting for other players...",
						AcceptText = "Accept Text",
						AcceptTextValue = "Listed below are offers you received.",
						AcceptButtonLabel = "Accept Button Label ",
						AcceptButtonLabelValue = "Continue" 
					):
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
