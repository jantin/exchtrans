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
from time import sleep

class rexOfferObj(object):
	"""A Data structure for holding participant offers"""
	def __init__(	self, 
					offeredX = None, 
					offeredY = None,
					offeredBy = None
				):
		self.offeredX = offeredX
		self.offeredY = offeredY
		self.offeredBy = offeredBy

class rexObj(object):
	"""A Data structure for holding parameters"""
	def __init__(	self, 
					p1x = 20, 
					p1y = 10,
					p1xValue = 5, 
					p1yValue = 1,
					p1xReplenish = 20,
					p1yReplenish = 10,
					p1Clearing = "End of exchange opportunity",
					p1xRequiredGift = 5,
					p1yRequiredGift = 5,
					p1RequireGift = False,
					p2x = 20, 
					p2y = 10,
					p2xValue = 5, 
					p2yValue = 1,
					p2xReplenish = 20,
					p2yReplenish = 10,				
					p2Clearing = "End of exchange opportunity", 
					p2xRequiredGift = 5,
					p2yRequiredGift = 5,
					p2RequireGift = False,
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
		self.p1xRequiredGift = p1xRequiredGift
		self.p1yRequiredGift = p1yRequiredGift
		self.p1RequireGift = p1RequireGift
		self.p2x = p2x
		self.p2y = p2y
		self.p2xValue = p2xValue
		self.p2yValue = p2yValue
		self.p2xReplenish = p2xReplenish
		self.p2yReplenish = p2yReplenish
		self.p2Clearing = p2Clearing
		self.p2xRequiredGift = p2xRequiredGift
		self.p2yRequiredGift = p2yRequiredGift
		self.p2RequireGift = p2RequireGift
		self.showPoints = showPoints
		self.widgets = widgets

@login_required
def rexEdit(request):
	"""Accepts the rex component form and updates the database"""
	comID = request.POST.get("comIM")
	
	if(request.POST.get("showPoints") == "on"):
		showPoints = True
	else:
		showPoints = False

	if(request.POST.get("p1RequireGift") == "on"):
		p1RequireGift = True
	else:
		p1RequireGift = False

	if(request.POST.get("p2RequireGift") == "on"):
		p2RequireGift = True
	else:
		p2RequireGift = False

	widgetCount = request.POST.get("widgetCount")
	widgets = []
	for i in range(int(widgetCount)):
		try:
			widgets.append(int(request.POST.get("widgetSelect_" + str(i+1))))
		except:
			pass
		
	
	componentParams = rexObj(
								p1x = request.POST.get("p1x"),
								p1y = request.POST.get("p1y"),
								p1xValue = request.POST.get("p1xValue"),
								p1yValue = request.POST.get("p1yValue"),
								p1xReplenish = request.POST.get("p1xReplenish"),
								p1yReplenish = request.POST.get("p1yReplenish"),
								p1Clearing = request.POST.get("p1Clearing"),
								p1xRequiredGift = request.POST.get("p1xRequiredGift"),
								p1yRequiredGift = request.POST.get("p1yRequiredGift"),
								p1RequireGift = p1RequireGift,
								p2x = request.POST.get("p2x"),
								p2y = request.POST.get("p2y"),
								p2xValue = request.POST.get("p2xValue"),
								p2yValue = request.POST.get("p2yValue"),
								p2xReplenish = request.POST.get("p2xReplenish"),
								p2yReplenish = request.POST.get("p2yReplenish"),
								p2Clearing = request.POST.get("p2Clearing"),
								p2xRequiredGift = request.POST.get("p2xRequiredGift"),
								p2yRequiredGift = request.POST.get("p2yRequiredGift"),
								p2RequireGift = p2RequireGift,
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



@login_required
def rexDisplay(request):
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
	
	# Serialize the rex object into a dictionary that can be passed as JSON
	exchangeParametersJSON = {}
	for key,value in request.session['exchangeParameters'].__dict__.items():
		exchangeParametersJSON[key] = value
	exchangeParametersJSON = simplejson.dumps(exchangeParametersJSON)
		
	# Get the player pairing map
	playerPairMapKey = "matcher_" + str(request.session['c'].id) + "_" + str(request.session['p'].currentComponent) + "_playerPairMap"
	playerPairMap = SessionVar.objects.get(key=playerPairMapKey).value
	request.session['playerPairMap'] = pickle.loads(playerPairMap)
	
	# Get the current pairing index. The -1 is because the PairingIndex is incremented by the matcher just before we get here
	request.session['currentPairingIndex'] = request.session['playerPairMap'][request.session['p'].number] - 1
	
	# Get the current pairing. Random pairings are in the Session Var table. Non-random pairings are stored in the matcher component
	if(request.session['parameters'].randomPairing == True):
		RandomPairsKey = "matcher_" + str(request.session['c'].id) + "_" + str(request.session['p'].currentComponent) + "_RandomPairs"
		RandomPairs = SessionVar.objects.get(experimentSession=request.session['s'],key=RandomPairsKey)
		RandomPairs = pickle.loads(RandomPairs.value)
		request.session['pairings'] = RandomPairs
		request.session['currentPairing'] = RandomPairs[int(request.session['currentPairingIndex'])]
	else:
		request.session['pairings'] = request.session['parameters'].pairings
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
		request.session['xValue'] = int(request.session['exchangeParameters'].p1xValue)
		request.session['yValue'] = int(request.session['exchangeParameters'].p1yValue)
	elif (int(request.session['currentPairing']["p2"]) == int(request.session['p'].number)):
		request.session['playerNumber'] = 2
		request.session['startingX'] = int(request.session['exchangeParameters'].p2x)
		request.session['startingY'] = int(request.session['exchangeParameters'].p2y)
		request.session['replenishX'] = int(request.session['exchangeParameters'].p2xReplenish)
		request.session['replenishY'] = int(request.session['exchangeParameters'].p2yReplenish)
		request.session['clearing'] = request.session['exchangeParameters'].p2Clearing
		request.session['currentX'] = int(request.session['exchangeParameters'].p2x)
		request.session['currentY'] = int(request.session['exchangeParameters'].p2y)
		request.session['xValue'] = int(request.session['exchangeParameters'].p2xValue)
		request.session['yValue'] = int(request.session['exchangeParameters'].p2yValue)
	else:
		request.session['playerNumber'] = None

	
	# Get widget content
	widgets = prepareWidgets(request.session['exchangeParameters'].widgets)
	
	return render_to_response("rex/rex_display.html", 
							{	'opponentIdentity': request.session['opponent'].identityLetter,
								'exchangeParametersJSON': exchangeParametersJSON,
								'playerNumber': request.session['playerNumber'],
								'widgets': widgets,
								'startingX': request.session['startingX'],
								'startingY': request.session['startingY'],
								'showXYValue': request.session['exchangeParameters'].showPoints,
								'xValue': request.session['xValue'],
								'yValue': request.session['yValue']
							}, 
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
	
	jsonString = simplejson.dumps(response)
	return render_to_response('api.html', 
						  {'response': jsonString}, 
						  context_instance=RequestContext(request))

def offerFormulation(request):
	"""Records the offer (gift) of the player and sends them to the waiting screen"""
	
	response = {}
	response['processor'] = "offerFormulation"
	
	# Error check input. Must be integer greater than zero. int conversion strips leading 'O's
	if(len(request.POST.get('offerFormulationOfferX')) == 0):
		offeredX = "0"
	else:
		offeredX = int(request.POST.get('offerFormulationOfferX'))
		offeredX = str(offeredX)
	if(len(request.POST.get('offerFormulationOfferY')) == 0):
		offeredY = "0"
	else:
		offeredY = int(request.POST.get('offerFormulationOfferY'))
		offeredY = str(offeredY)
		
	offerObj = rexOfferObj(	offeredX = offeredX,
							offeredY = offeredY,
							offeredBy = request.session['p'].name
						   )
	offerInsertKey = request.session['keyPrefix'] + "_offerFrom_" + request.session['p'].name
	offerInsert = SessionVar(experimentSession=request.session['s'], key=offerInsertKey, value=pickle.dumps(offerObj)).save()
	
	# Update the players X and Y
	request.session['currentX'] -= int(offerObj.offeredX)
	response['setX'] = request.session['currentX']	
	request.session['currentY'] -= int(offerObj.offeredY)
	response['setY'] = request.session['currentY']
	
	response['continuePolling'] = False
	response['resetFormulationForms'] = True
	response['showScreen'] = "waitingScreen"
	response['poll'] = True
	response['url'] = "/rex/waitingScreenPollProcess/"
	response['interval'] = 2000

		
	jsonString = simplejson.dumps(response)
	return render_to_response('api.html', 
						  {'response': jsonString}, 
						  context_instance=RequestContext(request))


def waitingScreenPollProcess(request):
	"""Polls to see if the other player has offered"""
	response = {}	
	response['processor'] = "waitingScreenPollProcess"
	offerCheckKey = request.session['keyPrefix'] + "_offerFrom_" + request.session['opponent'].name
	try:
		offerCheck = SessionVar.objects.get(key=offerCheckKey, unread=True)
	except:
		response['continuePolling'] = True
	else:
		offerObj = pickle.loads(offerCheck.value)
		
		response['showScreen'] = "transactionSummary"
		response['stopTimer'] = True
		response['continuePolling'] = False
		
		# Add the X and Y from the other player to the player's X and Y stash
		request.session['currentX'] += int(offerObj.offeredX)
		response['setX'] = request.session['currentX']	
		request.session['currentY'] += int(offerObj.offeredY)
		response['setY'] = request.session['currentY']
				
		response['updateBank'] = request.session['p'].cumulativePoints
			
		offerCheck.unread = False
		offerCheck.save()
	
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
		response['url'] = "/rex/nextRoundCountdownPollProcess/"
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

		
	
	
	
	
