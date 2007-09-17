from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import Context, Template, RequestContext
from django.core.exceptions import ObjectDoesNotExist
from django.utils import simplejson
from models import *
from common import *
from views import *
import pickle
from time import time

class nexObj(object):
	"""A Data structure holding a negotiated exchange object"""
	def __init__(	self, 
					p1x = 20, 
					p1y = 10,
					p1xValue = 5, 
					p1yValue = 1,
					p1xReplenish = 20,
					p1yReplenish = 10,
					p1Clearing = "End of round",
					p2x = 20, 
					p2y = 10,
					p2xValue = 5, 
					p2yValue = 1,
					p2xReplenish = 20,
					p2yReplenish = 10,					
					p2Clearing = "End of round",
					mins = 2,
					secs = 30,
					nonBinding = False,
					showPoints = False
				):
		self.p1x = p1x
		self.p1y = p1y
		self.p1xValue = p1xValue
		self.p1yValue = p1yValue
		self.p1xReplenish = p1xReplenish
		self.p1yReplenish = p1yReplenish
		self.p1Clearing = p1Clearing
		self.p2x = p2x
		self.p2y = p2y
		self.p2xValue = p2xValue
		self.p2yValue = p2yValue
		self.p2xReplenish = p2xReplenish
		self.p2yReplenish = p2yReplenish
		self.p2Clearing = p2Clearing
		self.mins = mins
		self.secs = secs
		self.nonBinding = nonBinding
		self.showPoints = showPoints


@login_required
def nexDisplay(request):
	"""Displays the negotiated exchange"""
	sid = request.GET.get('sid')
	pname = request.GET.get('pname')
	opponentName = request.GET.get('opponentName')
	exchangeComponentID = request.GET.get('exchangeComponentID')
	
	# get the current Participant object, session vars, and matcher params
	p = Participant.objects.get(name=pname)
	s = ExperimentSession.objects.get(id=sid)
	cumulativePoints = p.cumulativePoints
	sesVars = loadSessionVars(sid)
	# Note: these parameters are for the matcher component that is calling the current exchange component
	parameters = pickle.loads(sesVars.componentsList[int(p.currentComponent)].component_id.parameters)
	# Note: This component object is for the matcher component that is calling the current exchange component
	c = sesVars.componentsList[int(p.currentComponent)].component_id

	# get the current exchange component parameters
	exchangeParameters = pickle.loads(Component.objects.get(id=51).parameters)
	# Serialize the nex object into a dictionary that can be passed as JSON
	exchangeParametersJSON = {}
	for key,value in exchangeParameters.__dict__.items():
		exchangeParametersJSON[key] = value
	exchangeParametersJSON = simplejson.dumps(exchangeParametersJSON)

	# Get the current pairing
	playerPairMapKey = "matcher" + str(c.id) + "playerPairMap"
	playerPairMap = SessionVar.objects.get(key=playerPairMapKey).value
	playerPairMap = pickle.loads(playerPairMap)
	currentPairingIndex = playerPairMap[p.number]
	currentPairing = parameters.pairings[currentPairingIndex]
	
	# get the identity of the other player
	opponentIdentity = Participant.objects.get(name=opponentName).identityLetter
	
	# Register current player as being ready
	# key form is playerReady_<currentComponentID>_<exchangeComponentID>_<pairingIndex>_<pname>
	key = "playerReady_" + str(c.id) + "_" + exchangeComponentID + "_" + str(currentPairingIndex) + "_" + pname
	sv = SessionVar(key=key, value="True", experimentSession=s)
	sv.save()
	
	# Determine if the current player is player 1 or player 2 of the pairing
	if (int(currentPairing["p1"]) == int(p.number)):
		playerNumber = 1
	elif (int(currentPairing["p2"]) == int(p.number)):
		playerNumber = 2
	else:
		playerNumber = None
	
	print exchangeParameters.p2xValue
	
	return render_to_response("nex/nex_display.html", 
							{	'sid': sid, 
								'pname': pname,
								'parameters': parameters,
								'cumulativePoints': cumulativePoints,
								'opponentName': opponentName,
								'exchangeComponentID': exchangeComponentID,
								'opponentIdentity': opponentIdentity,
								'exchangeParameters': exchangeParameters,
								'exchangeParametersJSON': exchangeParametersJSON,
								'playerNumber': playerNumber
								
							}, 
						  	context_instance=RequestContext(request))

@login_required
def nexEdit(request):
	"""Saves the contents of the negotiated exchange component form"""
		
	comID = request.POST.get("comIM")
	
	if(request.POST.get("nonBinding") == "on"):
		nonBinding = True
	else:
		nonBinding = False
	
	if(request.POST.get("showPoints") == "on"):
		showPoints = True
	else:
		showPoints = False
	
	componentParams = nexObj(
								p1x = request.POST.get("p1x"),
								p1y = request.POST.get("p1y"),
								p1xValue = request.POST.get("p1xValue"),
								p1yValue = request.POST.get("p1yValue"),
								p1xReplenish = request.POST.get("p1xReplenish"),
								p1yReplenish = request.POST.get("p1yReplenish"),
								p1Clearing = request.POST.get("p1Clearing"),
								p2x = request.POST.get("p2x"),
								p2y = request.POST.get("p2y"),
								p2xValue = request.POST.get("p2xValue"),
								p2yValue = request.POST.get("p2yValue"),
								p2xReplenish = request.POST.get("p2xReplenish"),
								p2yReplenish = request.POST.get("p2yReplenish"),
								p2Clearing = request.POST.get("p2Clearing"),
								mins = request.POST.get("mins"),
								secs = request.POST.get("secs"),
								nonBinding = nonBinding,
								showPoints = showPoints
								)

	c = Component.objects.get(id=comID)
	c.name = request.POST.get("componentName")
	c.description = request.POST.get("componentDescription")
	c.displayName = request.POST.get("displayName")
	c.parameters = pickle.dumps(componentParams)
	c.save()
	
	response = "Component Saved"
	return render_to_response('api.html', 
						  {'response': response}, 
						  context_instance=RequestContext(request))


def checkForOpponentPollProcess(request):
	"""Handles the checkForOpponent screen."""
	sid = request.GET.get('sid')
	pname = request.GET.get('pname')
	opponentName = request.GET.get('opponentName')
	exchangeComponentID = request.GET.get('exchangeComponentID')
	
	
	# Initialize response dictionary
	response = {}
	response['processor'] = "checkForOpponentPollProcess"
	response['sid'] = sid
	response['pname'] = pname
	response['opponentName'] = opponentName
	response['exchangeComponentID'] = exchangeComponentID
	
	# get the current participant, component, and sesVars objects
	p = Participant.objects.get(name=pname)
	sesVars = loadSessionVars(sid)
	c = sesVars.componentsList[int(p.currentComponent)].component_id
	
	# Get the current pairing
	playerPairMapKey = "matcher" + str(c.id) + "playerPairMap"
	playerPairMap = SessionVar.objects.get(key=playerPairMapKey).value
	playerPairMap = pickle.loads(playerPairMap)
	currentPairingIndex = playerPairMap[p.number]
	
	# Check if opponent is ready.
	# key form is playerReady_<currentComponentID>_<exchangeComponentID>_<pairingIndex>_<pname>
	playerReadyKey = "playerReady_" + str(c.id) + "_" + exchangeComponentID + "_" + str(currentPairingIndex) + "_" + opponentName
	try:
		playerReady = SessionVar.objects.filter(key=playerReadyKey)[0].value
		if(playerReady == "True"):
			response['continuePolling'] = False
			response['showScreen'] = "makeOfferButton"
	except:
		response['continuePolling'] = True
		
	jsonString = simplejson.dumps(response)
	return render_to_response('api.html', 
						  {'response': jsonString}, 
						  context_instance=RequestContext(request))

def makeOfferButton(request):
	"""Handles the makeOfferButton form screen"""
	sid = request.POST.get('sid')
	pname = request.POST.get('pname')
	opponentName = request.POST.get('opponentName')
	exchangeComponentID = request.POST.get('exchangeComponentID')
	
	# Initialize response dictionary
	response = {}
	response['processor'] = "makeOfferButton"
	response['sid'] = sid
	response['pname'] = pname
	response['opponentName'] = opponentName
	response['exchangeComponentID'] = exchangeComponentID
	response['showScreen'] = "offerFormulation"
	
	
	jsonString = simplejson.dumps(response)
	return render_to_response('api.html', 
						  {'response': jsonString}, 
						  context_instance=RequestContext(request))

def offerFormulation(request):
	"""Handles the offerForumationScreen screen"""
	
	response = "Something"
	return render_to_response('api.html', 
						  {'response': response}, 
						  context_instance=RequestContext(request))


def counterOfferFormulation(request):
	"""Handles the counterOfferFormulation screen"""
	
	response = "Something"
	return render_to_response('api.html', 
						  {'response': response}, 
						  context_instance=RequestContext(request))


def waitingScreen(request):
	"""Handles the waitingScreen screen"""
	
	response = "Something"
	return render_to_response('api.html', 
						  {'response': response}, 
						  context_instance=RequestContext(request))


def confirmCancel(request):
	"""Handles the confirmCancel screen"""
	
	response = "Something"
	return render_to_response('api.html', 
						  {'response': response}, 
						  context_instance=RequestContext(request))


def incomingOffer(request):
	"""Handles the incomingOffer screen"""
	
	response = "Something"
	return render_to_response('api.html', 
						  {'response': response}, 
						  context_instance=RequestContext(request))


def confirmEndRound(request):
	"""Handles the confirmEndRound screen"""
	
	response = "Something"
	return render_to_response('api.html', 
						  {'response': response}, 
						  context_instance=RequestContext(request))


def nonBindingConfirmation(request):
	"""Handles the nonBindingConfirmation screen"""
	
	response = "Something"
	return render_to_response('api.html', 
						  {'response': response}, 
						  context_instance=RequestContext(request))


def transactionSummary(request):
	"""Handles the transactionSummary screen"""
	
	response = "Something"
	return render_to_response('api.html', 
						  {'response': response}, 
						  context_instance=RequestContext(request))


def nextRoundCountdown(request):
	"""Handles the nextRoundCountdown screen"""
	
	response = "Something"
	return render_to_response('api.html', 
						  {'response': response}, 
						  context_instance=RequestContext(request))

