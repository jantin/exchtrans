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
from etErrors import *

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


class nexOfferObj(object):
	"""A Data structure holding a negotiated exchange offer"""
	def __init__(	self, 
					offer, 
					offerUnit,
					request, 
					requestUnit,
					offeredBy
				):
		self.offer = offer
		self.offerUnit = offerUnit
		self.request = request
		self.requestUnit = requestUnit
		self.offeredBy = offeredBy

@login_required
def nexDisplay(request):
	"""Displays the negotiated exchange"""
	sid = request.GET.get('sid')
	pname = request.GET.get('pname')
	opponentName = request.GET.get('opponentName')
	exchangeComponentID = request.GET.get('exchangeComponentID')
	
	# get the current Participant object, session vars, and matcher params
	request.session['p'] = Participant.objects.get(name=pname)
	request.session['s'] = ExperimentSession.objects.get(id=sid)

	sesVars = loadSessionVars(sid)
	# Note: these parameters are for the matcher component that is calling the current exchange component
	request.session['parameters'] = pickle.loads(sesVars.componentsList[int(request.session['p'].currentComponent)].component_id.parameters)
	
	# Note: This component object is for the matcher component that is calling the current exchange component
	request.session['c'] = sesVars.componentsList[int(request.session['p'].currentComponent)].component_id

	# get the current exchange component parameters
	# TODO WHY is 51 hard coded?????
	request.session['exchangeParameters'] = pickle.loads(Component.objects.get(id=51).parameters)
	
	# Serialize the nex object into a dictionary that can be passed as JSON
	exchangeParametersJSON = {}
	for key,value in request.session['exchangeParameters'].__dict__.items():
		exchangeParametersJSON[key] = value
	exchangeParametersJSON = simplejson.dumps(exchangeParametersJSON)

	# Get the current pairing
	playerPairMapKey = "matcher" + str(request.session['c'].id) + "playerPairMap"
	playerPairMap = SessionVar.objects.get(key=playerPairMapKey).value
	request.session['playerPairMap'] = pickle.loads(playerPairMap)
	request.session['currentPairingIndex'] = request.session['playerPairMap'][request.session['p'].number]
	request.session['currentPairing'] = request.session['parameters'].pairings[int(request.session['currentPairingIndex'])]

	
	# get the identity of the other player
	request.session['opponent'] = Participant.objects.get(name=opponentName)

	# Set up a key prefix for reading and writing to the sessionvar table
	# The form is <currentComponentID>_<keyPrefix>_<pairingIndex>_<currentRound>
	request.session['keyPrefix'] = str(request.session['c'].id) + "_" + exchangeComponentID + "_" + str(request.session['currentPairingIndex']) + "_0" 

	# Register current player as being ready
	key = request.session['keyPrefix'] + "_playerReady_" + pname
	sv = SessionVar(key=key, value="True", experimentSession=request.session['s'])
	sv.save()
	
	
	# Determine if the current player is player 1 or player 2 of the pairing
	if (int(request.session['currentPairing']["p1"]) == int(request.session['p'].number)):
		request.session['playerNumber'] = 1
	elif (int(request.session['currentPairing']["p2"]) == int(request.session['p'].number)):
		request.session['playerNumber'] = 2
	else:
		request.session['playerNumber'] = None
		
	return render_to_response("nex/nex_display.html", 
							{	'opponentIdentity': request.session['opponent'].identityLetter,
								'exchangeParametersJSON': exchangeParametersJSON,
								'playerNumber': request.session['playerNumber']
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
	response = {}
	
	response['processor'] = "checkForOpponentPollProcess"

	# Check if opponent is ready.
	playerReadyKey = request.session['keyPrefix'] + "_playerReady_" + request.session['opponent'].name
	try:
		playerReady = SessionVar.objects.filter(key=playerReadyKey)[0].value
	except:
		response['continuePolling'] = True
	else:
		response['continuePolling'] = False
		response['showScreen'] = "makeOfferButton"
	
	jsonString = simplejson.dumps(response)
	return render_to_response('api.html', 
						  {'response': jsonString}, 
						  context_instance=RequestContext(request))

def makeOfferButton(request):
	"""Handles the makeOfferButton form screen"""
	response = {}
	response['processor'] = "makeOfferButton"
	response['showScreen'] = "offerFormulation"
	response['poll'] = True
	response['url'] = "/nex/checkForOfferPollProcess/"
	response['interval'] = 2000
	
	jsonString = simplejson.dumps(response)
	return render_to_response('api.html', 
						  {'response': jsonString}, 
						  context_instance=RequestContext(request))

def checkForOfferPollProcess(request):
	"""Check to see if the other player has made an offer. If so, interupt 
	the current player's offer forumlation and move to the incoming offer screen"""
	response = {}
	response['processor'] = "checkForOfferPollProcess"

	# Check for unread messages with the value offerMade
	messageKey = request.session['keyPrefix'] + "_messageTo_" + request.session['p'].name	
	try:
		message = SessionVar.objects.get(key=messageKey, value="offerMade") #, unread=True
	except:
		response['continuePolling'] = True
	else:
		# Change the status of the message to read
		message.unread = False
		message.save()
		response['continuePolling'] = False
		response['poll'] = True
		response['url'] = "/nex/checkForCancelWhileWaitingPollProcess/"
		response['interval'] = 2000
		response['showScreen'] = "incomingOffer"
	
	jsonString = simplejson.dumps(response)
	return render_to_response('api.html', 
						  {'response': jsonString}, 
						  context_instance=RequestContext(request))

def checkForCancelWhileWaitingPollProcess(request):
	"""Check to see if the other player has made an offer. If so, interupt 
	the current player's offer forumlation and move to the incoming offer screen"""
	response = {}
	response['processor'] = "checkForCancelWhileWaitingPollProcess"

	# Check for unread messages with the value offerMade
	messageKey = request.session['keyPrefix'] + "_messageTo_" + request.session['p'].name	
	try:
		message = SessionVar.objects.get(key=messageKey, unread=True, value="canceledWhileWaiting")
	except:
		response['continuePolling'] = True
	else:
		# Change the status of the message to read
		message.unread = False
		message.save()
		response['showScreen'] = "transactionSummary"
	
	jsonString = simplejson.dumps(response)
	return render_to_response('api.html', 
						  {'response': jsonString}, 
						  context_instance=RequestContext(request))


def offerFormulation(request):
	"""Handles the offerForumationScreen screen in the following way. First, check
	that an offer has not already been made. Then, insert the offer into the DB.
	Finally, if the current player is player 1, check that player 2 didn't sneak 
	an offer into the DB while player 1 was writing."""
	
	response = {}
	response['processor'] = "offerFormulation"	
	
	offerCheckKey = request.session['keyPrefix'] + "_messageTo_" + request.session['p'].name
	try:
		existingOffers = SessionVar.objects.filter(key=offerCheckKey)[0]
	except:
		offerObj = nexOfferObj(	offer=request.POST.get('offerFormulationOffer'), 
								offerUnit=request.POST.get('offerFormulationOfferUnit'), 
								request=request.POST.get('offerFormulationRequest'), 
								requestUnit=request.POST.get('offerFormulationRequestUnit'),
								offeredBy=request.session['p'].name
							   )
		offerInsertKey = request.session['keyPrefix'] + "_offerFrom_" + request.session['p'].name
		offerInsert = SessionVar(experimentSession=request.session['s'], key=offerInsertKey, value=pickle.dumps(offerObj)).save()
		
		messageToKey = request.session['keyPrefix'] + "_messageTo_" + request.session['opponent'].name
		messageTo = SessionVar(experimentSession=request.session['s'], key=messageToKey, value="offerMade").save()
		
		response['continuePolling'] = False
		response['showScreen'] = "waitingScreen"
		response['poll'] = True
		response['url'] = "/nex/waitingScreenPollProcess/"
		response['interval'] = 2000
	else:
		response['showScreen'] = "incomingOffer"
		response['continuePolling'] = False
	
	jsonString = simplejson.dumps(response)
	return render_to_response('api.html', 
						  {'response': jsonString}, 
						  context_instance=RequestContext(request))


def counterOfferFormulation(request):
	"""Handles the counterOfferFormulation screen"""
	response = {}
	response['processor'] = "counterOfferFormulation"	
	
	submit = request.POST.get('counterOfferFormulationSubmit')
	
	if(submit == "Cancel"):
		response['showScreen'] = "incomingOffer"
	elif(submit == "Counter Offer"):	
		offerObj = nexOfferObj(	offer=request.POST.get('offerFormulationOffer'), 
								offerUnit=request.POST.get('offerFormulationOfferUnit'), 
								request=request.POST.get('offerFormulationRequest'), 
								requestUnit=request.POST.get('offerFormulationRequestUnit'),
								offeredBy=request.session['p'].name
							   )
		offerInsertKey = request.session['keyPrefix'] + "_offerMade_" + request.session['p'].name
		offerInsert = SessionVar(experimentSession=request.session['s'], key=offerInsertKey, value=pickle.dumps(offerObj)).save()
		
		messageKey = request.session['keyPrefix'] + "_messageTo_" + request.session['opponent'].name
		message = SessionVar(experimentSession=request.session['s'], key=messageKey, value="counterOffered").save()
		
		response['showScreen'] = "waitingScreen"
		response['poll'] = True
		response['url'] = "/nex/waitingScreenPollProcess/"
		response['interval'] = 2000
	
	jsonString = simplejson.dumps(response)
	return render_to_response('api.html', 
						  {'response': jsonString}, 
						  context_instance=RequestContext(request))


def waitingScreen(request):
	"""Handles the waitingScreen screen"""
	response = {}
	response['processor'] = "waitingScreen"	
	response['showScreen'] = "confirmCancel"
	
	jsonString = simplejson.dumps(response)
	return render_to_response('api.html', 
						  {'response': jsonString}, 
						  context_instance=RequestContext(request))

def waitingScreenPollProcess(request):
	"""Polls to see if the other player has accepted the offer, counter offered, 
	or ended the round"""
	response = {}	
	response['processor'] = "waitingScreenPollProcess"
	key = request.session['keyPrefix'] + "_messageTo_" + request.session['p'].name
	messageValues = ["acceptNonBinding", "acceptBinding", "counterOffered", "endRound"]
	try:
		message = SessionVar.objects.get(key=key, unread=True, value__in=messageValues)
	except:
		response['continuePolling'] = True
	else:
		if(message.value == "acceptNonBinding"):
			response['showScreen'] = "nonBindingConfirmation"
		elif(message.value == "acceptBinding"):
			response['showScreen'] = "transactionSummary"
		elif(message.value == "counterOffered"):
			response['continuePolling'] = False
			response['poll'] = True
			response['url'] = "/nex/checkForCancelWhileWaitingPollProcess/"
			response['interval'] = 2000
			response['showScreen'] = "incomingOffer"
		elif(message.value == "endRound"):
			response['showScreen'] = "transactionSummary"
			
		response['continuePolling'] = False
		message.unread = False
		message.save()
	
	jsonString = simplejson.dumps(response)
	return render_to_response('api.html', 
						  {'response': jsonString}, 
						  context_instance=RequestContext(request))


def confirmCancel(request):
	"""Handles the confirmCancel screen"""
	confirmed = request.POST.get('confirmCancelSubmit')
	response = {}
	response['processor'] = "confirmCancel"
	
	if(confirmed == 'Yes'):
		key = request.session['keyPrefix'] + "_messageTo_" + request.session['opponent'].name
		SessionVar(key=key, experimentSession=request.session['s'], value="canceledWhileWaiting").save()
		response['showScreen'] = "transactionSummary"
		response['continuePolling'] = False
	elif(confirmed == 'No'):
		response['showScreen'] = "waitingScreen"
		
	jsonString = simplejson.dumps(response)
	return render_to_response('api.html', 
						  {'response': jsonString}, 
						  context_instance=RequestContext(request))


def incomingOffer(request):
	"""Handles the incomingOffer screen"""
	selection = request.POST.get('incomingOfferSubmit')
	response = {}
	response['processor'] = "incomingOffer"
	
	if(selection == "Accept"):
		key = request.session['keyPrefix'] + "_messageTo_" + request.session['opponent'].name
		if(request.session['exchangeParameters'].nonBinding):
			SessionVar(key=key, experimentSession=request.session['s'], value="acceptNonBinding").save()
			response['showScreen'] = "nonBindingConfirmation"
		else:
			SessionVar(key=key, experimentSession=request.session['s'], value="acceptBinding").save()
			response['showScreen'] = "transactionSummary"
	elif(selection == "Counter Offer"):
		response['showScreen'] = "counterOfferFormulation"
	elif(selection == "End Round"):
		response['showScreen'] = "confirmEndRound"
	
	jsonString = simplejson.dumps(response)
	return render_to_response('api.html', 
						  {'response': jsonString}, 
						  context_instance=RequestContext(request))


def confirmEndRound(request):
	"""Handles the confirmEndRound screen"""
	confirmed = request.POST.get('confirmEndRoundSubmit')
	response = {}
	response['processor'] = "confirmEndRound"
	
	if(confirmed == 'Yes'):
		key = request.session['keyPrefix'] + "_messageTo_" + request.session['opponent'].name
		SessionVar(key=key, experimentSession=request.session['s'], value="endRound").save()
		response['showScreen'] = "transactionSummary"
	elif(confirmed == 'No'):
		response['showScreen'] = "incomingOffer"
		
	jsonString = simplejson.dumps(response)
	return render_to_response('api.html', 
						  {'response': jsonString}, 
						  context_instance=RequestContext(request))


def nonBindingConfirmation(request):
	"""Handles the nonBindingConfirmation screen"""
	response = {}
	response['processor'] = "nonBindingConfirmation"
	
	
	jsonString = simplejson.dumps(response)
	return render_to_response('api.html', 
						  {'response': jsonString}, 
						  context_instance=RequestContext(request))


def transactionSummary(request):
	"""Handles the transactionSummary screen"""
	response = {}
	response['processor'] = "transactionSummary"
	
	jsonString = simplejson.dumps(response)
	return render_to_response('api.html', 
						  {'response': jsonString}, 
						  context_instance=RequestContext(request))


def nextRoundCountdown(request):
	"""Handles the nextRoundCountdown screen"""
	response = {}
	response['processor'] = "nextRoundCountdown"
	
	
	jsonString = simplejson.dumps(response)
	return render_to_response('api.html', 
						  {'response': jsonString}, 
						  context_instance=RequestContext(request))

		
	
	
	
	
	
	
