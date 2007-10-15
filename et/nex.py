from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import Context, Template, RequestContext
from django.core.exceptions import ObjectDoesNotExist
from django.utils import simplejson
from models import *
from common import *
from widgets import *
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
					p1xMaxRequest = 20,
					p1yMaxRequest = 10,
					p2x = 20, 
					p2y = 10,
					p2xValue = 5, 
					p2yValue = 1,
					p2xReplenish = 20,
					p2yReplenish = 10,					
					p2Clearing = "End of round",
					p2xMaxRequest = 20,
					p2yMaxRequest = 10,
					mins = 2,
					secs = 30,
					nonBinding = False,
					showPoints = False,
					widgets = []
				):
		self.p1x = p1x
		self.p1y = p1y
		self.p1xValue = p1xValue
		self.p1yValue = p1yValue
		self.p1xReplenish = p1xReplenish
		self.p1yReplenish = p1yReplenish
		self.p1Clearing = p1Clearing
		self.p1xMaxRequest = p1xMaxRequest
		self.p1yMaxRequest = p1yMaxRequest
		self.p2x = p2x
		self.p2y = p2y
		self.p2xValue = p2xValue
		self.p2yValue = p2yValue
		self.p2xReplenish = p2xReplenish
		self.p2yReplenish = p2yReplenish
		self.p2Clearing = p2Clearing
		self.p2xMaxRequest = p2xMaxRequest
		self.p2yMaxRequest = p2yMaxRequest
		self.mins = mins
		self.secs = secs
		self.nonBinding = nonBinding
		self.showPoints = showPoints
		self.widgets = widgets


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
	request.session['exchangeParameters'] = pickle.loads(Component.objects.get(id=exchangeComponentID).parameters)
	
	# Serialize the nex object into a dictionary that can be passed as JSON
	exchangeParametersJSON = {}
	for key,value in request.session['exchangeParameters'].__dict__.items():
		exchangeParametersJSON[key] = value
	exchangeParametersJSON = simplejson.dumps(exchangeParametersJSON)
		
	# Get the current pairing
	playerPairMapKey = "matcher" + str(request.session['c'].id) + "playerPairMap"
	playerPairMap = SessionVar.objects.get(key=playerPairMapKey).value
	request.session['playerPairMap'] = pickle.loads(playerPairMap)
	request.session['currentPairingIndex'] = request.session['playerPairMap'][request.session['p'].number] - 1
		# -1 because the PairingIndex is incremented by the matcher before we get here
	request.session['currentPairing'] = request.session['parameters'].pairings[int(request.session['currentPairingIndex'])]

	# Set the current exchange round to 1. (used to determine if another rounds in the current pairing is needed)
	request.session['currentRound'] = 1
	
	# get the identity of the other player
	request.session['opponent'] = Participant.objects.get(name=opponentName)

	# Set up a key prefix for reading and writing to the sessionvar table
	# The form is <currentComponentID>_<keyPrefix>_<pairingIndex>_<currentRound>
	request.session['keyPrefix'] = str(request.session['c'].id) + "_" + exchangeComponentID + "_" + str(request.session['currentPairingIndex']) + "_0" 

	# Register current player as being ready
	key = request.session['keyPrefix'] + "_playerReadyMessageTo_" + request.session['opponent'].name
	sv = SessionVar(key=key, value="True", experimentSession=request.session['s'])
	sv.save()
	
	# Determine if the current player is player 1 or player 2 of the pairing. Also grab the right starting X and Y quantities
	if (int(request.session['currentPairing']["p1"]) == int(request.session['p'].number)):
		request.session['playerNumber'] = 1
		request.session['startingX'] = int(request.session['exchangeParameters'].p1x)
		request.session['startingY'] = int(request.session['exchangeParameters'].p1y)
		request.session['replenishX'] = int(request.session['exchangeParameters'].p1xReplenish)
		request.session['replenishY'] = int(request.session['exchangeParameters'].p1yReplenish)
		request.session['clearing'] = request.session['exchangeParameters'].p1Clearing
		request.session['currentX'] = int(request.session['exchangeParameters'].p1x)
		request.session['currentY'] = int(request.session['exchangeParameters'].p1y)
	elif (int(request.session['currentPairing']["p2"]) == int(request.session['p'].number)):
		request.session['playerNumber'] = 2
		request.session['startingX'] = int(request.session['exchangeParameters'].p2x)
		request.session['startingY'] = int(request.session['exchangeParameters'].p2y)
		request.session['replenishX'] = int(request.session['exchangeParameters'].p2xReplenish)
		request.session['replenishY'] = int(request.session['exchangeParameters'].p2yReplenish)
		request.session['clearing'] = request.session['exchangeParameters'].p2Clearing
		request.session['currentX'] = int(request.session['exchangeParameters'].p2x)
		request.session['currentY'] = int(request.session['exchangeParameters'].p2y)
	else:
		request.session['playerNumber'] = None

	
	# Get widget content
	widgets = prepareWidgets(request.session['exchangeParameters'].widgets)
	
	return render_to_response("nex/nex_display.html", 
							{	'opponentIdentity': request.session['opponent'].identityLetter,
								'exchangeParametersJSON': exchangeParametersJSON,
								'playerNumber': request.session['playerNumber'],
								'widgets': widgets,
								'startingX': request.session['startingX'],
								'startingY': request.session['startingY']
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
	
	widgetCount = request.POST.get("widgetCount")
	widgets = []
	for i in range(int(widgetCount)):
		try:
			widgets.append(int(request.POST.get("widgetSelect_" + str(i+1))))
		except:
			pass
		
	
	componentParams = nexObj(
								p1x = request.POST.get("p1x"),
								p1y = request.POST.get("p1y"),
								p1xValue = request.POST.get("p1xValue"),
								p1yValue = request.POST.get("p1yValue"),
								p1xReplenish = request.POST.get("p1xReplenish"),
								p1yReplenish = request.POST.get("p1yReplenish"),
								p1Clearing = request.POST.get("p1Clearing"),
								p1xMaxRequest = request.POST.get("p1xMaxRequest"),
								p1yMaxRequest = request.POST.get("p1yMaxRequest"),
								p2x = request.POST.get("p2x"),
								p2y = request.POST.get("p2y"),
								p2xValue = request.POST.get("p2xValue"),
								p2yValue = request.POST.get("p2yValue"),
								p2xReplenish = request.POST.get("p2xReplenish"),
								p2yReplenish = request.POST.get("p2yReplenish"),
								p2Clearing = request.POST.get("p2Clearing"),
								p2xMaxRequest = request.POST.get("p2xMaxRequest"),
								p2yMaxRequest = request.POST.get("p2yMaxRequest"),
								mins = request.POST.get("mins"),
								secs = request.POST.get("secs"),
								nonBinding = nonBinding,
								showPoints = showPoints,
								widgets = widgets
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

	# Check for a ready message addressed to the player
	playerReadyKey = request.session['keyPrefix'] + "_playerReadyMessageTo_" + request.session['p'].name
	try:
		msg = SessionVar.objects.get(key=playerReadyKey,unread=True)
		msg.unread = False
		msg.save()
	except:
		response['continuePolling'] = True
	else:
		# check if the other player has set a start time message
		showTimeKey = request.session['keyPrefix'] + "_showTimeMessageTo_" + request.session['p'].name
		try:
			msg = SessionVar.objects.get(key=showTimeKey,unread=True)
			showTime = msg.value
			msg.unread = False
			msg.save()
		except:
			# If not, set a start time and write it in a message to the other participant
			# This synchronizes the timer's start time.
			showTimeKey = request.session['keyPrefix'] + "_showTimeMessageTo_" + request.session['opponent'].name
			showTime = int((time() + 3) * 1000)
			SessionVar(key=showTimeKey, value=showTime, experimentSession=request.session['s']).save()
			
		response['showTime'] = showTime
		response['continuePolling'] = False
		response['showScreen'] = "makeOfferButton"
		response['initBank'] = request.session['p'].cumulativePoints
		response['setX'] = request.session['startingX']
		response['setY'] = request.session['startingY']

				
	
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

	# Check for unread offer from opponent
	offerKey = request.session['keyPrefix'] + "_offerFrom_" + request.session['opponent'].name	
	try:
		offer = SessionVar.objects.get(key=offerKey, unread=True)
	except:
		response['continuePolling'] = True
	else:
		# Change the status of the message to read
		offer.unread = False
		offer.save()
		
		# unpickle the offer. Serialize the offer object into a dictionary that can be passed as JSON
		offerObj = pickle.loads(offer.value)
		offerJSON = {}
		for key,value in offerObj.__dict__.items():
			offerJSON[key] = value
		
		# While it's handy, save the offer to reqest.session
		request.session['currentOffer'] = offerObj
				
		response['incomingOffer'] = offerJSON
		response['continuePolling'] = False
		response['poll'] = True
		response['url'] = "/nex/checkForCancelWhileWaitingPollProcess/"
		response['interval'] = 2000
		response['showScreen'] = "incomingOffer"
		if(offerObj.requestUnit == "x"):
			if(int(offerObj.request) > request.session['currentX']):
				response['insufficientFunds'] = True
		else:
			if(int(offerObj.request) > request.session['currentY']):
				response['insufficientFunds'] = True
	
	jsonString = simplejson.dumps(response)
	return render_to_response('api.html', 
						  {'response': jsonString}, 
						  context_instance=RequestContext(request))

def checkForCancelWhileWaitingPollProcess(request):
	"""Check to see if the other player has canceled their offer while waiting for the other 
	player to accept, counter, or end the round"""
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
		response['transactionType'] = "opponentCanceledOffer"
		response['stopTimer'] = True
		response['continuePolling'] = False
		
	jsonString = simplejson.dumps(response)
	return render_to_response('api.html', 
						  {'response': jsonString}, 
						  context_instance=RequestContext(request))


def offerFormulation(request):
	"""Handles the offerForumationScreen screen in the following way. First, check
	that an offer has not already been made. Then, insert the offer into the DB.
	"""
	
	response = {}
	response['processor'] = "offerFormulation"	
	
	offerCheckKey = request.session['keyPrefix'] + "_offerFrom_" + request.session['opponent'].name
	try:
		existingOffer = SessionVar.objects.get(key=offerCheckKey, unread=True)
	except:
		offerObj = nexOfferObj(	offer=request.POST.get('offerFormulationOffer'), 
								offerUnit=request.POST.get('offerFormulationOfferUnit'), 
								request=request.POST.get('offerFormulationRequest'), 
								requestUnit=request.POST.get('offerFormulationRequestUnit'),
								offeredBy=request.session['p'].name
							   )
		offerInsertKey = request.session['keyPrefix'] + "_offerFrom_" + request.session['p'].name
		offerInsert = SessionVar(experimentSession=request.session['s'], key=offerInsertKey, value=pickle.dumps(offerObj)).save()
		
		offerJSON = {}
		for key,value in offerObj.__dict__.items():
			offerJSON[key] = value
		response['outgoingOffer'] = offerJSON
		
		# While it's handy, save the offer to reqest.session
		request.session['currentOffer'] = offerObj
		
		response['continuePolling'] = False
		response['showScreen'] = "waitingScreen"
		response['poll'] = True
		response['url'] = "/nex/waitingScreenPollProcess/"
		response['interval'] = 2000
	else:
		existingOffer.unread = False
		existingOffer.save()
		
		# unpickle the offer. Serialize the offer object into a dictionary that can be passed as JSON
		offerObj = pickle.loads(existingOffer.value)
		offerJSON = {}
		for key,value in offerObj.__dict__.items():
			offerJSON[key] = value
		
		# While it's handy, save the offer to reqest.session
		request.session['currentOffer'] = offerObj
				
		response['incomingOffer'] = offerJSON
		response['continuePolling'] = False
		response['poll'] = True
		response['url'] = "/nex/checkForCancelWhileWaitingPollProcess/"
		response['interval'] = 2000
		response['showScreen'] = "incomingOffer"
		if(offerObj.requestUnit == "x"):
			if(int(offerObj.request) > request.session['currentX']):
				response['insufficientFunds'] = True
		else:
			if(int(offerObj.request) > request.session['currentY']):
				response['insufficientFunds'] = True

		
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
		offerObj = nexOfferObj(	offer=request.POST.get('counterOfferFormulationOffer'), 
								offerUnit=request.POST.get('counterOfferFormulationOfferUnit'), 
								request=request.POST.get('counterOfferFormulationRequest'), 
								requestUnit=request.POST.get('counterOfferFormulationRequestUnit'),
								offeredBy=request.session['p'].name
							   )
		offerInsertKey = request.session['keyPrefix'] + "_offerFrom_" + request.session['p'].name
		offerInsert = SessionVar(experimentSession=request.session['s'], key=offerInsertKey, value=pickle.dumps(offerObj)).save()
		
		messageKey = request.session['keyPrefix'] + "_messageTo_" + request.session['opponent'].name
		message = SessionVar(experimentSession=request.session['s'], key=messageKey, value="counterOffered").save()
		
		offerJSON = {}
		for key,value in offerObj.__dict__.items():
			offerJSON[key] = value
		response['outgoingOffer'] = offerJSON
		
		# While it's handy, save the offer to reqest.session
		request.session['currentOffer'] = offerObj
		
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
			response['stopTimer'] = True
			response['transactionType'] = "opponentAccepted"
			response['continuePolling'] = False
			response['updateBank'] = request.session['p'].cumulativePoints
			
			# Figure out how much X and Y the player has left after the offer. The addition and
			# subtraction of X and Y is dependent on who made the offer.
			if(request.session['currentOffer'].offeredBy == request.session['p'].name):
				if(request.session['currentOffer'].offerUnit == "x"):
					request.session['currentX'] -= int(request.session['currentOffer'].offer)
					response['setX'] = request.session['currentX']
				else:
					request.session['currentY'] -= int(request.session['currentOffer'].offer)
					response['setY'] = request.session['currentY']
				if(request.session['currentOffer'].requestUnit == "x"):
					request.session['currentX'] += int(request.session['currentOffer'].request)
					response['setX'] = request.session['currentX']
				else:
					request.session['currentY'] += int(request.session['currentOffer'].request)
					response['setY'] = request.session['currentY']
			elif(request.session['currentOffer'].offeredBy == request.session['opponent'].name):
				if(request.session['currentOffer'].offerUnit == "x"):
					request.session['currentX'] += int(request.session['currentOffer'].offer)
					response['setX'] = request.session['currentX']
				else:
					request.session['currentY'] += int(request.session['currentOffer'].offer)
					response['setY'] = request.session['currentY']
				if(request.session['currentOffer'].requestUnit == "x"):
					request.session['currentX'] -= int(request.session['currentOffer'].request)
					response['setX'] = request.session['currentX']
				else:
					request.session['currentY'] -= int(request.session['currentOffer'].request)
					response['setY'] = request.session['currentY']
		elif(message.value == "counterOffered"):
			response['continuePolling'] = False
			response['poll'] = True
			response['url'] = "/nex/checkForCancelWhileWaitingPollProcess/"
			response['interval'] = 2000
			response['showScreen'] = "incomingOffer"

			# Grab the unread offer from opponent
			offerKey = request.session['keyPrefix'] + "_offerFrom_" + request.session['opponent'].name	
			offer = SessionVar.objects.get(key=offerKey, unread=True)

			# Change the status of the message to read
			offer.unread = False
			offer.save()

			# unpickle the offer. Serialize the offer object into a dictionary that can be passed as JSON
			offerObj = pickle.loads(offer.value)
			offerJSON = {}
			for key,value in offerObj.__dict__.items():
				offerJSON[key] = value
			response['incomingOffer'] = offerJSON
			
			# While it's handy, save the offer to reqest.session
			request.session['currentOffer'] = offerObj
			
			if(offerObj.requestUnit == "x"):
				if(int(offerObj.request) > request.session['currentX']):
					response['insufficientFunds'] = True
			else:
				if(int(offerObj.request) > request.session['currentY']):
					response['insufficientFunds'] = True
			
		elif(message.value == "endRound"):
			response['showScreen'] = "transactionSummary"
			response['stopTimer'] = True
			response['transactionType'] = "opponentEndedRound"
			response['continuePolling'] = False
			
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
		response['stopTimer'] = True
		response['transactionType'] = "youCanceledOffer"
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
			response['stopTimer'] = True
			response['transactionType'] = "youAccepted"
			response['continuePolling'] = False
			response['updateBank'] = request.session['p'].cumulativePoints
			
			# Figure out how much X and Y the player has left after the offer. The addition and
			# subtraction of X and Y is dependent on who made the offer.
			if(request.session['currentOffer'].offeredBy == request.session['p'].name):
				if(request.session['currentOffer'].offerUnit == "x"):
					request.session['currentX'] -= int(request.session['currentOffer'].offer)
					response['setX'] = request.session['currentX']
				else:
					request.session['currentY'] -= int(request.session['currentOffer'].offer)
					response['setY'] = request.session['currentY']
				if(request.session['currentOffer'].requestUnit == "x"):
					request.session['currentX'] += int(request.session['currentOffer'].request)
					response['setX'] = request.session['currentX']
				else:
					request.session['currentY'] += int(request.session['currentOffer'].request)
					response['setY'] = request.session['currentY']
			elif(request.session['currentOffer'].offeredBy == request.session['opponent'].name):
				if(request.session['currentOffer'].offerUnit == "x"):
					request.session['currentX'] += int(request.session['currentOffer'].offer)
					response['setX'] = request.session['currentX']
				else:
					request.session['currentY'] += int(request.session['currentOffer'].offer)
					response['setY'] = request.session['currentY']
				if(request.session['currentOffer'].requestUnit == "x"):
					request.session['currentX'] -= int(request.session['currentOffer'].request)
					response['setX'] = request.session['currentX']
				else:
					request.session['currentY'] -= int(request.session['currentOffer'].request)
					response['setY'] = request.session['currentY']
			
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
		response['transactionType'] = "youEndedTheRound"
		response['stopTimer'] = True
		response['continuePolling'] = False
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
	"""Handles the transactionSummary screen's continue button"""
	
	earnedPoints = request.POST.get("transactionSummaryPoints")
	
	# Save the participant's points in the database
	participantObj = Participant.objects.get(name=request.session['p'].name)
	participantObj.cumulativePoints += int(earnedPoints)
	participantObj.save()
	
	# Save the participant points in request.session
	request.session['p'].cumulativePoints += int(earnedPoints) 
	request.session.modified = True
	
	response = {}
	response['processor'] = "transactionSummary"
	
	# Figure out if they're doing another round or moving on to the next pairing
	request.session['currentRound'] += 1
	if(int(request.session['currentRound']) > int(request.session['currentPairing']['rounds'])):
		# If going on to the next pairing, redirect to the matcher display function which will figure out what to do next
		response['redirect'] = "/matcher/display/?sid=" + str(request.session['s'].id) + "&pname=" + request.session['p'].name + "&increment=1"
	else:
		# Moving on to the next round. Write a message that the player is ready
		playerReadyKey = request.session['keyPrefix'] + "_readyForNextRoundMessageTo_" + request.session['opponent'].name
		SessionVar(key=playerReadyKey, value="Ready", experimentSession=request.session['s']).save()
		
		# send to the nextRoundCountdown screen and start a poll process
		response['showScreen'] = "nextRoundCountdown"
		response['poll'] = True
		response['url'] = "/nex/nextRoundCountdownPollProcess/"
		response['interval'] = 2000
	
	jsonString = simplejson.dumps(response)
	return render_to_response('api.html', 
						  {'response': jsonString}, 
						  context_instance=RequestContext(request))

def nextRoundCountdownPollProcess(request):
	"""Waits for the other player to click continue after transaction summary screen."""
	response = {}
	
	response['processor'] = "nextRoundCountdownPollProcess"

	# Check if opponent is ready.
	playerReadyKey = request.session['keyPrefix'] + "_readyForNextRoundMessageTo_" + request.session['p'].name
	try:
		msg = SessionVar.objects.get(key=playerReadyKey,unread=True)
		msg.unread = False
		msg.save()
	except:
		response['continuePolling'] = True
	else:
		# check if the other player has set a start time message
		showTimeKey = request.session['keyPrefix'] + "_showTimeMessageTo_" + request.session['p'].name
		try:
			msg = SessionVar.objects.get(key=showTimeKey,unread=True)
			showTime = msg.value
			msg.unread = False
			msg.save()
		except:
			# If not, set a start time and write it in a message to the other participant
			showTimeKey = request.session['keyPrefix'] + "_showTimeMessageTo_" + request.session['opponent'].name
			showTime = int((time() + 3) * 1000)
			SessionVar(key=showTimeKey, value=showTime, experimentSession=request.session['s']).save()
			
		response['showTime'] = showTime
		response['continuePolling'] = False
		response['showScreen'] = "makeOfferButton"	
		response['initBank'] = request.session['p'].cumulativePoints
		
		# Give the player the right amount of X and Y
		if(request.session['clearing'] == "End of exchange opportunity"):
			request.session['currentX'] = request.session['replenishX']
			request.session['currentY'] = request.session['replenishY']
			response['setX'] = request.session['currentX']
			response['setY'] = request.session['currentY']
		elif(request.session['clearing'] == "End of pairing"):
			request.session['currentX'] += request.session['replenishX']
			request.session['currentY'] += request.session['replenishY']
			response['setX'] = request.session['currentX']
			response['setY'] = request.session['currentY']
	
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

		
	
	
	
	
