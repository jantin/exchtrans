from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import Context, Template, RequestContext
from django.core.exceptions import ObjectDoesNotExist
from models import *
from common import *
from views import *
import pickle
from time import time
from random import shuffle

class matcherObj(object):
	"""A Data structure holding a matcher."""
	def __init__(	self, 
					pairings = [{'p1': "0", 'p2': "1", 'decider': "0", 'rounds': "1", 'choices':[]}],
					randomPairing = True,
					randomChoices = [],
					randomRounds = "1"
				):
		self.pairings = pairings
		self.randomPairing = randomPairing
		self.randomChoices = randomChoices
		self.randomRounds = randomRounds
		'''
		If randomPairing is set to true, pairing and pair1rounds
		are ignored at runtime.
		
		The pairing stucture works as such:
		[{player 1, Player 2, Decider, rounds},...]
		
		Decider is one of the following
		1, indicating player 1
		2, indicating player 2
		0, indicating no decider (first selected component will be used)
		'''


@login_required
def matcherDisplay(request):
	"""Displays the matcher"""
		
	sid = request.GET.get('sid')
	pname = request.GET.get('pname')
	
	# get the current Participant object
	p = Participant.objects.get(name=pname)
	cumulativePoints = p.cumulativePoints
	sesVars = loadSessionVars(sid)
	parameters = pickle.loads(sesVars.componentsList[int(p.currentComponent)].component_id.parameters)
	
	# get the current session object
	s = ExperimentSession.objects.get(id=sid)
	# get the current component object
	c = sesVars.componentsList[int(p.currentComponent)].component_id

	# Log start time
	logWrite(	participant = p, 
				component = c, 
				session = s,
				messageType = "timestamp",
				messageText = "start"
				)
	
	# Log component Type
	logWrite(	participant = p, 
				component = c, 
				session = s,
				messageType = "componentType",
				messageText = c.componentType
				)

	# Log component paramerters
	logWrite(	participant = p, 
				component = c, 
				session = s,
				messageType = "componentParams",
				messageText = pickle.dumps(parameters)
				)
	
	
	
	# check to see if participant is involved in pairing and if not, send ahead
	#if( (parameters.randomPairing == False) and not checkPairsForPlayer(parameters.pairing, p.number) ):
	#	return HttpResponseRedirect('/session/drive/?pname=' + p.name + '&sid=' + sid)
	
	# if random, create pairings (first player to get here only)
	# first, check if the pairings have been created already
	if( parameters.randomPairing ):
		# check if the pairings have been created already by checking for
		# a session variable in the SessionVar table.
		
		# This key may be problematic if the experiment contains the same component multiple times
		key = "matcher" + str(c.id) + "RandomPairs"
		try:
			pairsCheck = SessionVar.objects.get(experimentSession=s,key=key)
		except:
			pairsCheck = False
		
		# if not, create random pairings
		if (pairsCheck == False):
			# roundRobin runs twice. On the first pass, everyone is paired with everyone and 
			# player 1 is the decider. On the second pass, everyone is paired with everyone
			# and player 2 is the decider.
			shuffledPlayers = shuffle(range(len(sesVars.participantsList)-1))
			pairs = roundRobin( shuffledPlayers, decider = 0 )
			pairs += roundRobin( shuffledPlayers, decider = 1 )
			sv = SessionVar(experimentSession=s, key=key, value=pickle.dumps(pairs))
			sv.save()
	'''
	else:
		# Get the identity of the other player in the pair
		opponentIdentity = getOpponentIdentity(parameters.pairing, p.number, sid)
		
		# check if there is a decider involved
		if( checkForDecider(parameters.pairing) ):
			# is the current player the decider?
			if ( checkPlayerIsDecider(parameters.pairing, p.number) ):
				
				# Get a list of possible components
				choices = []
				for choice in parameters.pair1ComponentChoices:
					choices.append(Component.objects.get(id=choice))
				
				# Send to decider choice screen
				return render_to_response("matcher/matcher_decider.html", 
										{	'sid': sid, 
											'pname': pname,
											'parameters': parameters,
											'choices': choices,
											'opponentIdentity': opponentIdentity
										}, 
									  	context_instance=RequestContext(request))
			else:
				# send to non decider screen
				return render_to_response("matcher/matcher_nonDecider.html", 
										{	'sid': sid, 
											'pname': pname,
											'parameters': parameters,
											'opponentIdentity': opponentIdentity											
										}, 
									  	context_instance=RequestContext(request))
		else:
			# There is no decider, therefore direct the player to the first of the selected
			# decider choices. If there is no decider specified, there should be only one selected.
			
			choiceID = parameters.pair1ComponentChoices[0]
			
			# get the component object
			chosenComponent = Component.objects.get(id=choiceID)

			# Determine the kick off function for the component
			kickOffFunction = chosenComponent.componentType.kickoffFunction

			# redirect to the kickoff function of the component
			return HttpResponseRedirect('/' + kickOffFunction + '/?pname=' + pname + '&sid=' + sid)		
	'''
	# Send off to first random pairing
	# iterate throught the pairs list looking for a pairing the current player is involved with
	# Check if that player is a decider or not, if so pass to matcher_decider, otherwise: matcher_nonDecider
	# Write a session var indicating the current pairing index and the player's id
	# Write a new function that exchange forms direct to after the exchange is complete that checks what pairing the player is currently on moves them to the next OR passes to driveSession
	return render_to_response("textPage/textPage_display.html", 
							{	'sid': sid, 
								'pname': pname,
								'parameters': parameters,
								'cumulativePoints': cumulativePoints
							}, 
						  	context_instance=RequestContext(request))

@login_required
def deciderSubmit(request):
	"""Handles the deciders exchange choice by writing the choice to the SessionVar table
		and starting the decider on the chosen component. """
	choiceID = request.POST.get("deciderChoice")
	sid = request.POST.get('sid')
	pname = request.POST.get('pname')
	
	# get the current Participant object
	p = Participant.objects.get(name=pname)
	
	# get the current session object
	s = ExperimentSession.objects.get(id=sid)
	# get the current component object
	sesVars = loadSessionVars(sid)
	c = sesVars.componentsList[int(p.currentComponent)].component_id
	# get the choice component object
	chosenComponent = Component.objects.get(id=choiceID)
	
	# Make a key and write to the SessionVar table
	key = "deciderChoice_" + str(c.id) + "_" + str(p.identityLetter)
	sv = SessionVar(experimentSession=s, key=key, value=choiceID)
	sv.save()
	
	# Determine the kick off function for the chosen component
	kickOffFunction = chosenComponent.componentType.kickoffFunction
	
	# redirect to the kickoff function of the chosen component
	return HttpResponseRedirect('/' + kickOffFunction + '/?pname=' + pname + '&sid=' + sid)
	

def checkDeciderChoice(request):
	"""The non decider calls this function to see if the decider has chosen."""
	# Make the key and check if it exists in the SessionVar table
	opponentIdentity = request.GET.get("opponentIdentity")
	sid = request.GET.get('sid')
	pname = request.GET.get('pname')
	
	# get the current Participant object
	p = Participant.objects.get(name=pname)
	
	# get the current session object
	s = ExperimentSession.objects.get(id=sid)
	# get the current component object
	sesVars = loadSessionVars(sid)
	c = sesVars.componentsList[int(p.currentComponent)].component_id
	
	key = "deciderChoice_" + str(c.id) + "_" + opponentIdentity
	try:
		choiceCheck = SessionVar.objects.get(experimentSession=s,key=key)
	except:
		choiceCheck = False
	
	if(choiceCheck == False):
		return render_to_response('api.html', 
								  {'response': ""}, 
								  context_instance=RequestContext(request))
	else:
		return render_to_response('api.html', 
								  {'response': choiceCheck.value}, 
								  context_instance=RequestContext(request))

def followDecider(request):
	"""This function puts the non-decider into the component chosen by the decider."""
	choiceID = request.GET.get("choiceID")
	sid = request.GET.get('sid')
	pname = request.GET.get('pname')
	
	# get the choice component object
	chosenComponent = Component.objects.get(id=choiceID)
	
	# Determine the kick off function for the chosen component
	kickOffFunction = chosenComponent.componentType.kickoffFunction
	
	# redirect to the kickoff function of the chosen component
	return HttpResponseRedirect('/' + kickOffFunction + '/?pname=' + pname + '&sid=' + sid)
	

@login_required
def matcherEdit(request):
	"""Saves the contents of the matcher form"""
	comID = request.POST.get("comIM")
	# Slightly different form handling depending on the random pairing checkbox
	if(request.POST.get("randomPairingCheck") == "on"):
		componentParams = matcherObj(
									randomPairing = True,
									randomRounds = request.POST.get("randomRounds"),
									randomChoices = request.POST.getlist("randomChoices")
									)
	else:
		pairingCount = request.POST.get("pairingCount")
		pairings = []
		for i in range(int(pairingCount)):
			pairings.append	(
								{ 	'p1': request.POST.get("p1_" + str(i)),
									'p2': request.POST.get("p2_" + str(i)),
									'decider': request.POST.get("decider_" + str(i)),
									'rounds': request.POST.get("rounds_" + str(i)),
									'choices': request.POST.getlist("componentChoices_" + str(i))
								}
							)
		componentParams = matcherObj(
										randomPairing = False,
										pairings = pairings
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


def roundRobin(units, decider=0, sets=None):
	""" Generates a schedule of "fair" pairings from a list of units """
	# pulled from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/65200
	if len(units) % 2:
		units.append(None)
	count	 = len(units)
	sets	 = sets or (count - 1)
	half	 = count / 2
	schedule = []
	for turn in range(sets):
		pairings = []
		for i in range(half):
			pairings.append({'p1': units[i], 'p2': units[count-i-1], 'decider':decide})
			# pairings.append([units[i], units[count-i-1], decide])
		units.insert(1, units.pop())
		schedule.append(pairings)
	return schedule

def checkPairsForPlayer(pairing, playerNumber):
	"""Accepts a pairing list and a player number. Returns true if player 
		is involved in the pairing and false if the player if not involved"""
	for pair in pairing:
		if( pair[0] == str(playerNumber) or pair[1] == str(playerNumber) ):
			return True
	return False

def checkForDecider(pair):
	"""Checks if the given pairing has a decider. Returns True if there is a decider
		False if there is not a decider"""
	print "DECIDER VALUE:" + str(pair[0][2])
	if( int(pair[0][2]) > 0 ):
		return True
	else:
		return False
	
def checkPlayerIsDecider(pair, playerNumber):
	"""Checks if the given player is the decider in the given pair"""
	decider = int(pair[0][2]) - 1
	if( pair[0][decider] == str(playerNumber) ):
		return True
	else:
		return False

def getOpponentIdentity(pair, playerNumber, sid):
	"""Accepts a pairing and a player number. Returns the identity Letter of the 
		other player in the pairing """
	p1 = pair[0][0]
	p2 = pair[0][1]
	playerNumber = str(playerNumber)
	
	if(playerNumber == p1):
		opponent = Participant.objects.get(experimentSession=sid, number=p2)
		return opponent.identityLetter
	elif(playerNumber == p2):
		opponent = Participant.objects.get(experimentSession=sid, number=p1)
		return opponent.identityLetter
	else:
		return False
	
	
	
	
	
	
	
	
	