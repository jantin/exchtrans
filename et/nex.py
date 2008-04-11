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
  def __init__( self, 
          p1x = 20, 
          p1y = 10,
          p1xValue = 5, 
          p1yValue = 1,
          p1xReplenish = 20,
          p1yReplenish = 10,
          p1Clearing = "End of exchange opportunity",
          p1xMaxRequest = 20,
          p1yMaxRequest = 10,
          p2x = 20, 
          p2y = 10,
          p2xValue = 5, 
          p2yValue = 1,
          p2xReplenish = 20,
          p2yReplenish = 10,          
          p2Clearing = "End of exchange opportunity",
          p2xMaxRequest = 20,
          p2yMaxRequest = 10,
          mins = 2,
          secs = 30,
          nonBinding = False,
          showPoints = False,
          resetPoints = False,
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
    self.resetPoints = resetPoints # added by n8
    self.widgets = widgets

class nexOfferObj(object):
  """A Data structure holding a negotiated exchange offer"""
  def __init__( self, 
          offer = None, 
          offerUnit = None,
          request = None, 
          requestUnit = None,
          offeredBy = None
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
  request.session['exchangeComponentID'] = request.GET.get('exchangeComponentID')
  
  # get the current Participant object, session vars, and matcher params
  request.session['p'] = Participant.objects.get(name=pname)
  request.session['s'] = ExperimentSession.objects.get(id=sid)
  
  sesVars = loadSessionVars(sid)
  # Note: these parameters are for the matcher component that is calling the current exchange component
  request.session['parameters'] = pickle.loads(sesVars.componentsList[int(request.session['p'].currentComponent)].component_id.parameters)
  
  # Note: This component object is for the matcher component that is calling the current exchange component
  request.session['c'] = sesVars.componentsList[int(request.session['p'].currentComponent)].component_id
  
  # get the current exchange component parameters
  request.session['exchangeParameters'] = pickle.loads(Component.objects.get(id=request.session['exchangeComponentID']).parameters)
  
  # Serialize the nex object into a dictionary that can be passed as JSON
  exchangeParametersJSON = {}
  for key,value in request.session['exchangeParameters'].__dict__.items():
    exchangeParametersJSON[key] = value
  exchangeParametersJSON = simplejson.dumps(exchangeParametersJSON)
  
  # Get the player pairing map
  playerPairMapKey = "matcher_" + str(request.session['c'].id) + "_" + str(request.session['p'].currentComponent) + "_playerPairMap"
  playerPairMap = SessionVar.objects.get(key=playerPairMapKey, experimentSession=request.session['s']).value
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
  
  # Set the current offer index to 1. Used for logging purposes.
  request.session['offerIndex'] = 1
  
  # get the identity of the other player
  request.session['opponent'] = Participant.objects.get(name=opponentName)
  
  # Set up a key prefix for reading and writing to the sessionvar table
  # The form is <currentMatcherComponentID>_<currentExchangeComponentID>_<pairingIndex>_<currentRound>
  request.session['keyPrefix'] = str(request.session['c'].id) + "_" + request.session['exchangeComponentID'] + "_" + str(request.session['currentPairingIndex']) + "_0" 
  
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
  
  # Set the initial poll URL
  setPollURL(request, "/nex/checkForOpponentPollProcess/")
  
  # Get widget content
  widgets = prepareWidgets(request.session['exchangeParameters'].widgets)
  
  
  return render_to_response("nex/nex_display.html", 
              { 'opponentIdentity': request.session['opponent'].identityLetter,
                'exchangeParametersJSON': exchangeParametersJSON,
                'playerNumber': request.session['p'].number,
                # 'playerNumber': request.session['playerNumber'],
                'opponentNumber': request.session['opponent'].number,
                'widgets': widgets,
                'startingX': request.session['startingX'],
                'startingY': request.session['startingY'],
                'showXYValue': request.session['exchangeParameters'].showPoints,
                'xValue': request.session['xValue'],
                'yValue': request.session['yValue']
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
  
  if(request.POST.get("resetPoints") == "on"):
    resetPoints = True
  else:
    resetPoints = False
  
  widgetCount = request.POST.get("widgetCount")
  widgets = []
  for i in range(int(widgetCount)):
    try:
      widgets.append(int(request.POST.get("widgetSelect_" + str(i+1))))
    except:
      pass
    
  
  componentParams = nexObj( p1x = request.POST.get("p1x"),
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
                resetPoints = resetPoints,
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
    msg = SessionVar.objects.get(key=playerReadyKey,unread=True, experimentSession=request.session['s'])
    msg.unread = False
    msg.save()
  except:
    pass
  else:
    # check if the other player has set a start time message
    showTimeKey = request.session['keyPrefix'] + "_showTimeMessageTo_" + request.session['p'].name
    try:
      msg = SessionVar.objects.get(key=showTimeKey,unread=True, experimentSession=request.session['s'])
      showTime = msg.value
      msg.unread = False
      msg.save()
    except:
      # If not, set a start time and write it in a message to the other participant
      # This synchronizes the timer's start time.
      showTimeKey = request.session['keyPrefix'] + "_showTimeMessageTo_" + request.session['opponent'].name
      showTime = int((time() + 3) * 1000)
      SessionVar(key=showTimeKey, value=showTime, experimentSession=request.session['s']).save()
    
    # Set the initial poll URL
    setPollURL(request, "None")
    
    response['showTime'] = showTime
    response['showScreen'] = "makeOfferButton"
    response['initBank'] = request.session['p'].cumulativePoints
    response['setX'] = str(request.session['startingX'])
    response['setY'] = str(request.session['startingY'])
  
  jsonString = simplejson.dumps(response)
  return render_to_response('api.html', 
              {'response': jsonString}, 
              context_instance=RequestContext(request))

def makeOfferButton(request):
  """Handles the makeOfferButton form screen"""
  response = {}
  response['processor'] = "makeOfferButton"
  response['resetFormulationForms'] = True
  response['showScreen'] = "offerFormulation"
  
  # n8: I moved this block of code that handles the timer start from the
  # checkForOpponentPollProcess method because the timer was starting before
  # the user was actually attempting to make a negotiation.
  # This presents a problem, in that a user who clicks the "Click to begin"
  # button prior to the other gets to start making an offer without the timer
  # starting. That's because the timer starts only when both users are
  # synchronized.
  # On the other hand, you can think of this as not a necessarily
  # bad thing since the objective is not to time the individuals, but to
  # incentivise them to make a decision.
  #
  # check if the other player has set a start time message
  # showTimeKey = request.session['keyPrefix'] + "_showTimeMessageTo_" + request.session['p'].name
  # try:
  #   msg = SessionVar.objects.get(key=showTimeKey,unread=True, experimentSession=request.session['s'])
  #   showTime = msg.value
  #   msg.unread = False
  #   msg.save()
  # except:
  #   # If not, set a start time and write it in a message to the other participant
  #   # This synchronizes the timer's start time.
  #   showTimeKey = request.session['keyPrefix'] + "_showTimeMessageTo_" + request.session['opponent'].name
  #   showTime = int((time() + 3) * 1000)
  #   SessionVar(key=showTimeKey, value=showTime, experimentSession=request.session['s']).save()
  # 
  # response['showTime'] = showTime
  
  setPollURL(request, "/nex/checkForOfferPollProcess/")
  
  jsonString = simplejson.dumps(response)
  return render_to_response('api.html', 
              {'response': jsonString}, 
              context_instance=RequestContext(request))

def getPollURL(request):
  """Grabs the current poll URL from the session var table and returns it."""
  response = {}
  response['processor'] = "getPollURL"
  
  key = request.session['keyPrefix'] + "_pollURLFor_" + request.session['p'].name 
  try:
    pollURL = SessionVar.objects.get(key=key, experimentSession=request.session['s']).value
  except:
    response['pollURL'] = "None"
  else:
    response['pollURL'] = pollURL
  
  response['key'] = key
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
    offer = SessionVar.objects.get(key=offerKey, unread=True, experimentSession=request.session['s'])
  except:
    pass
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
    
    # set up a log_nex object. It will be completed and saved later depending on the outcome
    request.session['logEntry'] = init_log_nex(request)
    request.session['logEntry'].initiatedOffer = 0
    
    # Not checking for cancel while waiting because it's not fully implemented
    # setPollURL(request, "/nex/checkForCancelWhileWaitingPollProcess/")
    
    setPollURL(request, "None")
    
    response['showDialog'] = "incomingOffer"
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
  player to view the offer and then accept, counter, or end the round
  
  NOTE! this functionality is not fully implemented, therefore it's commented out elsewhere.
  
  """
  response = {}
  response['processor'] = "checkForCancelWhileWaitingPollProcess"
  
  # Check for unread messages with the value offerMade
  messageKey = request.session['keyPrefix'] + "_messageTo_" + request.session['p'].name 
  try:
    message = SessionVar.objects.get(key=messageKey, unread=True, value="canceledWhileWaiting", experimentSession=request.session['s'])
  except:
    pass
  else:
    # Change the status of the message to read
    message.unread = False
    message.save()
    response['showScreen'] = "transactionSummary"
    response['transactionType'] = "opponentCanceledOffer"
    response['stopTimer'] = True
    setPollURL(request, "None")
    
    # Write to the log
    request.session['logEntry'].outcome = "offerCanceled"
    request.session['logEntry'].save()
    # increment offerIndex
    request.session['offerIndex'] = 1
    
  
  jsonString = simplejson.dumps(response)
  return render_to_response('api.html', 
              {'response': jsonString}, 
              context_instance=RequestContext(request))

def offerFormulation(request):
  """Handles the offerForumationScreen screen in the following way. First, check
  that an offer has not already been made. Then, insert the offer into the DB.
  """
  setPollURL(request, "None")
  response = {}
  response['processor'] = "offerFormulation"
  
  # Lock the session var table while we check to see if there are any offers. Before removing
  # the lock, add the current player's offer in the case that there aren't any existing offers.
  from django.db import connection
  cursor = connection.cursor()
  cursor.execute("LOCK TABLES et_sessionvar WRITE, django_session WRITE, et_log_nex WRITE")
  
  offerCheckKey = request.session['keyPrefix'] + "_offerFrom_" + request.session['opponent'].name
  try:
    existingOffer = SessionVar.objects.get(key=offerCheckKey, unread=True, experimentSession=request.session['s'])
  except:
    # No existing offer found. Go ahead with the current player's offer.
    # Error check input. Must be integer greater than zero. int conversion strips leading 'O's
    if(len(request.POST.get('offerFormulationOffer')) == 0):
      offerAmount = "0"
    else:
      offerAmount = int(request.POST.get('offerFormulationOffer'))
      offerAmount = str(offerAmount)
    if(len(request.POST.get('offerFormulationRequest')) == 0):
      requestAmount = "0"
    else:
      requestAmount = int(request.POST.get('offerFormulationRequest'))
      requestAmount = str(requestAmount)
    
    offerObj = nexOfferObj( offer=offerAmount, 
                offerUnit=request.POST.get('offerFormulationOfferUnit'), 
                request=requestAmount, 
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
    
    
    # set up a log_nex object. It will be completed and saved later depending on the outcome
    request.session['logEntry'] = init_log_nex(request)
    request.session['logEntry'].initiatedOffer = 1
    
    response['resetFormulationForms'] = True
    response['showScreen'] = "waitingScreen"
    setPollURL(request, "/nex/waitingScreenPollProcess/")
  else:
    # Found an offer from the other player! 
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
    
    # set up a log_nex object. It will be completed and saved later depending on the outcome
    request.session['logEntry'] = init_log_nex(request)
    request.session['logEntry'].initiatedOffer = 0
    
    setPollURL(request, "/nex/checkForCancelWhileWaitingPollProcess/")
    response['showDialog'] = "incomingOffer"
    if(offerObj.requestUnit == "x"):
      if(int(offerObj.request) > request.session['currentX']):
        response['insufficientFunds'] = True
    else:
      if(int(offerObj.request) > request.session['currentY']):
        response['insufficientFunds'] = True
    
  
  cursor.execute("UNLOCK TABLES")
  
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
    
    # Error check input. Must be integer greater than zero. int conversion strips leading 'O's
    if(len(request.POST.get('counterOfferFormulationOffer')) == 0):
      offerAmount = "0"
    else:
      offerAmount = int(request.POST.get('counterOfferFormulationOffer'))
      offerAmount = str(offerAmount)
    if(len(request.POST.get('counterOfferFormulationRequest')) == 0):
      requestAmount = "0"
    else:
      requestAmount = int(request.POST.get('counterOfferFormulationRequest'))
      requestAmount = str(requestAmount)
          
    offerObj = nexOfferObj( offer=offerAmount, 
                offerUnit=request.POST.get('counterOfferFormulationOfferUnit'), 
                request=requestAmount, 
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
    
    # set up a log_nex object. It will be completed and saved later depending on the outcome
    request.session['logEntry'] = init_log_nex(request)
    request.session['logEntry'].initiatedOffer = 1
    
    
    response['resetFormulationForms'] = True
    response['showScreen'] = "waitingScreen"
    setPollURL(request, "/nex/waitingScreenPollProcess/")
  
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

def incomingOfferDeclinedToView(request):
  """Write a message to the other player telling them that the current player
  declined to view their offer"""
  key = request.session['keyPrefix'] + "_messageTo_" + request.session['opponent'].name
  SessionVar(key=key, experimentSession=request.session['s'], value="declinedToViewOffer").save()
  
  # Write to the log
  request.session['logEntry'].outcome = "declinedOffer"
  request.session['logEntry'].save()
  
  request.session['offerIndex'] += 1
  
  response = {}
  response['processor'] = "incomingOfferDeclinedToView" 
  response['showScreen'] = "offerFormulation"
  response['resetFormulationForms'] = True
  setPollURL(request, "/nex/checkForOfferPollProcess/")
    
  jsonString = simplejson.dumps(response)
  return render_to_response('api.html', 
              {'response': jsonString}, 
              context_instance=RequestContext(request))

def waitingScreenPollProcess(request):
  """Polls to see if the other player has declined to view the offer, accepted the offer, 
  counter offered, or ended the round"""
  response = {}
  request.session.modified = True # make sure request.session is saved
  response['processor'] = "waitingScreenPollProcess"
  key = request.session['keyPrefix'] + "_messageTo_" + request.session['p'].name
  messageValues = ["acceptNonBinding", "acceptBinding", "counterOffered", "endRound", "declinedToViewOffer"]
  try:
    message = SessionVar.objects.get(key=key, unread=True, value__in=messageValues, experimentSession=request.session['s'])
  except:
    pass
  else:
    if(message.value == "declinedToViewOffer"):
      response['showDialog'] = "offerDeclined"
      response['resetFormulationForms'] = True
      setPollURL(request, "/nex/checkForOfferPollProcess/")
      
      # Write to the log
      request.session['logEntry'].outcome = "offerDeclined"
      request.session['logEntry'].save()
      
      # increment the offer index
      request.session['offerIndex'] += 1
    elif(message.value == "acceptNonBinding"):
      response['showScreen'] = "nonBindingConfirmation"
      response['nonBindingOfferType'] = "OfferToOpponent"
      response['stopTimer'] = True
      setPollURL(request, "None")
      
      # Write to the log (don't save yet. We'll add followedThrough next, and save during the transaction summary.)
      request.session['logEntry'].outcome = "offerAccepted"
      
      # Reset the offer index
      request.session['offerIndex'] = 1
    elif(message.value == "acceptBinding"):
      response['showScreen'] = "transactionSummary"
      response['stopTimer'] = True
      response['transactionType'] = "opponentAccepted"
      setPollURL(request, "None")
      response['updateBank'] = request.session['p'].cumulativePoints
      
      # Write to the log (don't save yet. We'll add the pointChange and save at the transaction summary)
      request.session['logEntry'].outcome = "offerAccepted"
      
      # Reset the offer index
      request.session['offerIndex'] = 1
      
      # Figure out how much X and Y the player has left after the offer. The addition and
      # subtraction of X and Y is dependent on who made the offer.
      if(request.session['currentOffer'].offeredBy == request.session['p'].name):
        if(request.session['currentOffer'].offerUnit == "x"):
          request.session['currentX'] -= int(request.session['currentOffer'].offer)
          response['setX'] = str(request.session['currentX'])
        else:
          request.session['currentY'] -= int(request.session['currentOffer'].offer)
          response['setY'] = str(request.session['currentY'])
        if(request.session['currentOffer'].requestUnit == "x"):
          request.session['currentX'] += int(request.session['currentOffer'].request)
          response['setX'] = str(request.session['currentX'])
        else:
          request.session['currentY'] += int(request.session['currentOffer'].request)
          response['setY'] = str(request.session['currentY'])
      elif(request.session['currentOffer'].offeredBy == request.session['opponent'].name):
        if(request.session['currentOffer'].offerUnit == "x"):
          request.session['currentX'] += int(request.session['currentOffer'].offer)
          response['setX'] = str(request.session['currentX'])
        else:
          request.session['currentY'] += int(request.session['currentOffer'].offer)
          response['setY'] = str(request.session['currentY'])
        if(request.session['currentOffer'].requestUnit == "x"):
          request.session['currentX'] -= int(request.session['currentOffer'].request)
          response['setX'] = str(request.session['currentX'])
        else:
          request.session['currentY'] -= int(request.session['currentOffer'].request)
          response['setY'] = str(request.session['currentY'])
    elif(message.value == "counterOffered"):
      setPollURL(request, "/nex/checkForCancelWhileWaitingPollProcess/")
      response['showScreen'] = "incomingOffer"
      
      # Write to the log
      request.session['logEntry'].outcome = "offerCountered"
      request.session['logEntry'].save()
      # increment the offer index
      request.session['offerIndex'] += 1
      
      # Grab the unread offer from opponent
      offerKey = request.session['keyPrefix'] + "_offerFrom_" + request.session['opponent'].name  
      offer = SessionVar.objects.get(key=offerKey, unread=True, experimentSession=request.session['s'])
      
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
      
      # set up a log_nex object. It will be completed and saved later depending on the outcome
      request.session['logEntry'] = init_log_nex(request)
      request.session['logEntry'].initiatedOffer = 0
      
    elif(message.value == "endRound"):
      response['showScreen'] = "transactionSummary"
      response['stopTimer'] = True
      response['transactionType'] = "opponentEndedRound"
      setPollURL(request, "None")
      
      # Write to the log (don't save yet. The row will be saved after the transaction summary)
      request.session['logEntry'].outcome = "roundEnded"
      
      # Reset the offer index
      request.session['offerIndex'] = 1
      
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
    setPollURL(request, "None")
    key = request.session['keyPrefix'] + "_messageTo_" + request.session['opponent'].name
    SessionVar(key=key, experimentSession=request.session['s'], value="canceledWhileWaiting").save()
    response['showScreen'] = "transactionSummary"
    response['stopTimer'] = True
    response['transactionType'] = "youCanceledOffer"
    
    # Write to the log
    request.session['logEntry'].outcome = "canceledOffer"
    request.session['logEntry'].save()
    
    # Reset the offer index
    request.session['offerIndex'] = 1
    
  elif(confirmed == 'No'):
    response['showScreen'] = "waitingScreen"
    
  jsonString = simplejson.dumps(response)
  return render_to_response('api.html', 
              {'response': jsonString}, 
              context_instance=RequestContext(request))

def incomingOffer(request):
  """Handles the incomingOffer screen"""
  setPollURL(request, "None")
  selection = request.POST.get('incomingOfferSubmit')
  request.session.modified = True # Make sure we save request.session
  response = {}
  response['processor'] = "incomingOffer"
  
  if(selection == "Accept"):
    # Write to the log (don't save yet. Wait will transaction summary)
    request.session['logEntry'].outcome = "acceptedOffer"
    # reset offerIndex to 1
    request.session['offerIndex'] = 1
    
    key = request.session['keyPrefix'] + "_messageTo_" + request.session['opponent'].name
    if(request.session['exchangeParameters'].nonBinding):
      SessionVar(key=key, experimentSession=request.session['s'], value="acceptNonBinding").save()
      response['showScreen'] = "nonBindingConfirmation"
      response['nonBindingOfferType'] = "OfferFromOpponent"
      response['stopTimer'] = True
    else:
      SessionVar(key=key, experimentSession=request.session['s'], value="acceptBinding").save()
      response['showScreen'] = "transactionSummary"
      response['stopTimer'] = True
      response['transactionType'] = "youAccepted"
      response['updateBank'] = request.session['p'].cumulativePoints
      
      # Figure out how much X and Y the player has left after the offer. The addition and
      # subtraction of X and Y is dependent on who made the offer.
      if(request.session['currentOffer'].offeredBy == request.session['p'].name):
        if(request.session['currentOffer'].offerUnit == "x"):
          request.session['currentX'] -= int(request.session['currentOffer'].offer)
          response['setX'] = str(request.session['currentX'])
        else:
          request.session['currentY'] -= int(request.session['currentOffer'].offer)
          response['setY'] = str(request.session['currentY'])
        if(request.session['currentOffer'].requestUnit == "x"):
          request.session['currentX'] += int(request.session['currentOffer'].request)
          response['setX'] = str(request.session['currentX'])
        else:
          request.session['currentY'] += int(request.session['currentOffer'].request)
          response['setY'] = str(request.session['currentY'])
      elif(request.session['currentOffer'].offeredBy == request.session['opponent'].name):
        if(request.session['currentOffer'].offerUnit == "x"):
          request.session['currentX'] += int(request.session['currentOffer'].offer)
          response['setX'] = str(request.session['currentX'])
        else:
          request.session['currentY'] += int(request.session['currentOffer'].offer)
          response['setY'] = str(request.session['currentY'])
        if(request.session['currentOffer'].requestUnit == "x"):
          request.session['currentX'] -= int(request.session['currentOffer'].request)
          response['setX'] = str(request.session['currentX'])
        else:
          request.session['currentY'] -= int(request.session['currentOffer'].request)
          response['setY'] = str(request.session['currentY'])
      
  elif(selection == "Counter Offer"):
    # Write to the log
    request.session['logEntry'].outcome = "counterOffered"
    request.session['logEntry'].save()
    # increment offerIndex
    request.session['offerIndex'] += 1
    
    response['showScreen'] = "counterOfferFormulation"
  elif(selection == "End Round"):
    # Write to the log
    request.session['logEntry'].outcome = "endedRound"
    request.session['logEntry'].save()
    # reset offerIndex to 1
    request.session['offerIndex'] = 1
    
    response['showScreen'] = "confirmEndRound"
  
  jsonString = simplejson.dumps(response)
  return render_to_response('api.html', 
              {'response': jsonString}, 
              context_instance=RequestContext(request))

# n8: this is a hack to deal with the timer ending in a NEX exchange
# and create some record of it in the database.  it also takes a line
# from the offerFormulation method which checks for any outstanding offers
# and leaves them in the db, but marks them as read.  not happy about the
# way this works... surprise!
def timerRanOut(request):
  request.session['logEntry'] = init_log_nex(request)
  request.session['logEntry'].xGain = request.session['currentX']
  request.session['logEntry'].yGain = request.session['currentY']
  request.session['logEntry'].xLoss = 0
  request.session['logEntry'].yLoss = 0
  request.session['logEntry'].outcome = "timerRanOut"
  request.session['logEntry'].save()

  # try to find the offer
  offerCheckKey = request.session['keyPrefix'] + "_offerFrom_" + request.session['opponent'].name
  try:
    existingOffer = SessionVar.objects.get(key=offerCheckKey, unread=True, experimentSession=request.session['s'])
  except:
    pass # if the offer doesn't exist do nothing
  else:
    # mark the existing offer as read
    existingOffer.unread = False
    existingOffer.save()

  response = {}
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
    setPollURL(request, "None")
    key = request.session['keyPrefix'] + "_messageTo_" + request.session['opponent'].name
    SessionVar(key=key, experimentSession=request.session['s'], value="endRound").save()
    response['showScreen'] = "transactionSummary"
    response['transactionType'] = "youEndedTheRound"
    response['stopTimer'] = True
  elif(confirmed == 'No'):
    response['showScreen'] = "incomingOffer"
    # reset the session log object so that the 'endedRound' log doesn't get
    # deleted
    request.session['logEntry'] = init_log_nex(request)
    request.session['logEntry'].initiatedOffer = 0
    
  jsonString = simplejson.dumps(response)
  return render_to_response('api.html', 
              {'response': jsonString}, 
              context_instance=RequestContext(request))

def nonBindingConfirmation(request):
  """Handles the nonBindingConfirmation screen"""
  choice = request.POST.get('nonBindingConfirmationSubmit')
  request.session.modified = True # Make sure we save session.request
  response = {}
  response['processor'] = "nonBindingConfirmation"
  response['stopTimer'] = True
  response['showScreen'] = "nonBindingWaitingScreen"
  setPollURL(request, "/nex/nonBindingPollProcess/")
  
  key = request.session['keyPrefix'] + "_nonBindingMessageTo_" + request.session['opponent'].name 
  
  if(choice == 'Yes'):
    SessionVar(key=key, experimentSession=request.session['s'], value="followedThrough").save()
    response['transactionType'] = "followedThrough"
    request.session['didIFollowThrough'] = True
    request.session['logEntry'].followedThrough = 1
  elif(choice == 'No'):
    SessionVar(key=key, experimentSession=request.session['s'], value="reneged").save()
    response['transactionType'] = "reneged"
    request.session['didIFollowThrough'] = False
    request.session['logEntry'].followedThrough = 0
    
  jsonString = simplejson.dumps(response)
  return render_to_response('api.html', 
              {'response': jsonString}, 
              context_instance=RequestContext(request))

def nonBindingPollProcess(request):
  """Polls to see if the other player made a selection on the nonBinding Screen"""
  response = {} 
  response['processor'] = "nonBindingPollProcess"
  
  key = request.session['keyPrefix'] + "_nonBindingMessageTo_" + request.session['p'].name  
  messageValues = ["followedThrough", "reneged"]
  try:
    message = SessionVar.objects.get(key=key, unread=True, value__in=messageValues, experimentSession=request.session['s'])
  except:
    pass
  else:
    setPollURL(request, "None")
    # Determine how much X and Y the player has after the transaction. 
    # 1) Check if the other player followed through or reneged
    if(message.value == "followedThrough"):
      
      # 2) Check if the current player followed through or reneged
      if(request.session['didIFollowThrough']):
        response['transactionType'] = "youFollowedThroughOpponentFollowedThrough"
        
        # 3) Check if the offer is from the current player or the opponent
        if(request.session['currentOffer'].offeredBy == request.session['p'].name):
          # Get the unit letter
          offerXY = request.session['currentOffer'].offerUnit.upper()
          requestXY = request.session['currentOffer'].requestUnit.upper()
          # Update the request session
          request.session['current' + offerXY]  -= int(request.session['currentOffer'].offer)
          request.session['current' + requestXY]  += int(request.session['currentOffer'].request)
          # Update the players X and Y totals
          response['set' + offerXY] = request.session['current' + offerXY]
          response['set' + requestXY] = request.session['current' + requestXY]
        elif(request.session['currentOffer'].offeredBy == request.session['opponent'].name):
          # Get the unit letter
          offerXY   = request.session['currentOffer'].offerUnit.upper()
          requestXY   = request.session['currentOffer'].requestUnit.upper()
          # Update the request session
          request.session['current' + offerXY]  += int(request.session['currentOffer'].offer)
          request.session['current' + requestXY]  -= int(request.session['currentOffer'].request)
          # Update the players X and Y totals
          response['set' + offerXY]   = request.session['current' + offerXY]
          response['set' + requestXY] = request.session['current' + requestXY]
      else:
        response['transactionType'] = "youRenegedOpponentFollowedThrough"
        if(request.session['currentOffer'].offeredBy == request.session['p'].name):
          requestXY = request.session['currentOffer'].requestUnit.upper()
          request.session['current' + requestXY]  += int(request.session['currentOffer'].request)
          response['set' + requestXY] = request.session['current' + requestXY]
          request.session['currentOffer'].offer = 0
        elif(request.session['currentOffer'].offeredBy == request.session['opponent'].name):
          offerXY   = request.session['currentOffer'].offerUnit.upper()
          request.session['current' + offerXY]  += int(request.session['currentOffer'].offer)
          response['set' + offerXY]   = request.session['current' + offerXY]
          request.session['currentOffer'].request = 0
    elif(message.value == "reneged"):
      if(request.session['didIFollowThrough']):
        response['transactionType'] = "youFollowedThroughOpponentReneged"
        if(request.session['currentOffer'].offeredBy == request.session['p'].name):
          offerXY = request.session['currentOffer'].offerUnit.upper()
          request.session['current' + offerXY]  -= int(request.session['currentOffer'].offer)
          response['set' + offerXY] = request.session['current' + offerXY]
          request.session['currentOffer'].request = 0
        elif(request.session['currentOffer'].offeredBy == request.session['opponent'].name):
          requestXY   = request.session['currentOffer'].requestUnit.upper()
          request.session['current' + requestXY]  -= int(request.session['currentOffer'].request)
          response['set' + requestXY] = request.session['current' + requestXY]
          request.session['currentOffer'].offer = 0
      else:
        response['transactionType'] = "youRenegedOpponentReneged"
        request.session['currentOffer'].request = 0
        request.session['currentOffer'].offer = 0
    
    # If the offer was changed because a player reneged
    if(not response['transactionType'] == "youFollowedThroughOpponentFollowedThrough"):   
      offerJSON = {}
      for key,value in request.session['currentOffer'].__dict__.items():
        offerJSON[key] = value
      
      if(request.session['currentOffer'].offeredBy == request.session['opponent'].name):
        modifiedOfferKey = request.session['keyPrefix'] + "_modifiedOfferFrom_" + request.session['opponent'].name  
        response['incomingOffer'] = offerJSON
      else:
        modifiedOfferKey = request.session['keyPrefix'] + "_modifiedOfferFrom_" + request.session['p'].name 
        response['outgoingOffer'] = offerJSON
    
      #Save the modified session into the Session Var table in case it's useful later
      SessionVar(key=modifiedOfferKey, experimentSession=request.session['s'], value=pickle.dumps(request.session['currentOffer'])).save()
    
      # save the modified offer into request.session
      request.session.modified = True
    
    response['showScreen'] = "transactionSummary"
    response['updateBank'] = request.session['p'].cumulativePoints
    
    message.unread = False
    message.save()
  
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
  
  request.session['logEntry'].pointChange = earnedPoints
  request.session['logEntry'].save()
  
  # Figure out if they're doing another round or moving on to the next pairing
  request.session['currentRound'] += 1
  if(int(request.session['currentRound']) > int(request.session['currentPairing']['rounds'])):
    # If going on to the next pairing, redirect to the matcher display function which will figure out what to do next
    
    # n8 add block
    # Figure out if this is just a practice round and if so, reset the points
    if (request.session['exchangeParameters'].resetPoints):
      request.session['logEntry'].outcome = "endedPracticeRound"
      request.session['logEntry'].pointChange = 0
      request.session['logEntry'].save()
      
      # I guess this resets the local cumulativePoints?  Not really sure...
      request.session['p'].cumulativePoints = 0
    
      # Save the participant's points in the database
      participantObj = Participant.objects.get(name=request.session['p'].name)
      participantObj.cumulativePoints = 0
      participantObj.save()
    
    response['redirect'] = "/matcher/display/?sid=" + str(request.session['s'].id) + "&pname=" + request.session['p'].name + "&increment=1"
  else:
    # Moving on to the next round. Write a message that the player is ready
    playerReadyKey = request.session['keyPrefix'] + "_readyForNextRoundMessageTo_" + request.session['opponent'].name
    SessionVar(key=playerReadyKey, value="Ready", experimentSession=request.session['s']).save()
    
    # send to the nextRoundCountdown screen and start a poll process
    response['showScreen'] = "nextRoundCountdown"
    setPollURL(request, "/nex/nextRoundCountdownPollProcess/")
  
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
    msg = SessionVar.objects.get(key=playerReadyKey,unread=True, experimentSession=request.session['s'])
    msg.unread = False
    msg.save()
  except:
    pass
  else:
    setPollURL(request, "None")
    # check if the other player has set a start time message
    showTimeKey = request.session['keyPrefix'] + "_showTimeMessageTo_" + request.session['p'].name
    try:
      msg = SessionVar.objects.get(key=showTimeKey,unread=True, experimentSession=request.session['s'])
      showTime = msg.value
      msg.unread = False
      msg.save()
    except:
      # If not, set a start time and write it in a message to the other participant
      showTimeKey = request.session['keyPrefix'] + "_showTimeMessageTo_" + request.session['opponent'].name
      showTime = int((time() + 3) * 1000)
      SessionVar(key=showTimeKey, value=showTime, experimentSession=request.session['s']).save()
      
    response['showTime'] = showTime
    response['showScreen'] = "makeOfferButton"  
    response['initBank'] = request.session['p'].cumulativePoints
    
    # Give the player the right amount of X and Y
    if(request.session['clearing'] == "End of exchange opportunity"):
      request.session['currentX'] = request.session['replenishX']
      request.session['currentY'] = request.session['replenishY']
    elif(request.session['clearing'] == "End of pairing"):
      request.session['currentX'] += request.session['replenishX']
      request.session['currentY'] += request.session['replenishY']
    
    response['setX'] = str(request.session['currentX'])
    response['setY'] = str(request.session['currentY'])
    request.session['startingX'] = request.session['replenishX']
    request.session['startingY'] = request.session['replenishY']
    
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

def setPollURL(request, pollURL):
  """Quick method to set the poll URL"""
  pollURLKey = request.session['keyPrefix'] + "_pollURLFor_" + request.session['p'].name
  # Try to grab the pollURL row from the session var table. If it's not there, create it, otherwise update it.
  try:
    row = SessionVar.objects.get(experimentSession=request.session['s'], key=pollURLKey)
  except:
    SessionVar(experimentSession=request.session['s'], key=pollURLKey, value=pollURL).save()
  else:
    row.value = pollURL
    row.save()
    return True

def init_log_nex(request):
  """Sets up a log_nex object"""
  log_nex_init = log_nex( sid=request.session['s'].id,
              cid=request.session['exchangeComponentID'],
              componentIndex=request.session['p'].currentComponent+1,
              roundIndex=request.session['currentRound'],
              offerIndex=request.session['offerIndex'],
              participantName=request.session['p'].name,
              participantPartner=request.session['opponent'].name,
              startingX=request.session['startingX'],
              startingY=request.session['startingY'],
              xValue=request.session['xValue'],
              yValue=request.session['yValue'],
              nonBinding=request.session['exchangeParameters'].nonBinding
              )
  if(request.session['currentOffer'].offerUnit == "x"):
    log_nex_init.xGain = request.session['currentOffer'].offer
    log_nex_init.yGain = 0
  else:
    log_nex_init.xGain = 0
    log_nex_init.yGain = request.session['currentOffer'].offer
  if(request.session['currentOffer'].requestUnit == "x"):
    log_nex_init.xLoss = request.session['currentOffer'].request
    log_nex_init.yLoss = 0
  else:
    log_nex_init.xLoss = 0
    log_nex_init.yLoss = request.session['currentOffer'].request
  
  return log_nex_init
