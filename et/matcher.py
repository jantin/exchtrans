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
		[{player 1, Player 2, Decider, rounds, choices},...]
		
		Decider is one of the following
		1, indicating player 1
		2, indicating player 2
		0, indicating no decider (first selected component in choices list will be used)
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
	
	# if random, create pairings (first player to get here only)
	# first, check if the pairings have been created already
	if( parameters.randomPairing ):
		# check if the pairings have been created already by checking for
		# a session variable in the SessionVar table.
		
		RandomPairsKey = "matcher_" + str(c.id) + "_" + str(p.currentComponent) + "_RandomPairs"
		try:
			pairings = SessionVar.objects.get(experimentSession=s,key=RandomPairsKey)
			pairings = pickle.loads(pairings.value)
		except:
			# roundRobin runs twice. On the first pass, everyone is paired with everyone and 
			# player 1 is the decider. On the second pass, everyone is paired with everyone
			# and player 2 is the decider.
			players = range(len(sesVars.participantsList))
			shuffle(players)
			pairings = roundRobin( units = players, decider = 1, rounds = parameters.randomRounds, choices = parameters.randomChoices )
			pairings += roundRobin( units = players, decider = 2, rounds = parameters.randomRounds, choices = parameters.randomChoices )
			RandomPairsSessionVar = SessionVar(experimentSession=s, key=RandomPairsKey, value=pickle.dumps(pairings))
			RandomPairsSessionVar.save()
			
			# Write the random pairings to the log.
			log = log_components.objects.get(sid=sid, componentIndex=p.currentComponent+1)
			logParams = pickle.loads(log.componentParameters)
			logParams.pairings = pairings
			log.componentParameters = pickle.dumps(logParams)
			log.save()
	else:
		pairings = parameters.pairings

	# Check for the playerPairMap in the sessionVar table. Create if not found.
	playerPairMapKey = "matcher_" + str(c.id) + "_" + str(p.currentComponent) + "_playerPairMap"
	try:
		playerPairMapSessionVar = SessionVar.objects.get(experimentSession=s,key=playerPairMapKey)
		playerPairMap = pickle.loads(playerPairMapSessionVar.value)
	except:
		# PlayerPairMap uses the player number as a key to the current pairing index. The pairing index indicates
		# where we are in the pairings list of the matcherObj.
		playerPairMap = {}
		players = range(len(sesVars.participantsList))
		for i in players:
			playerPairMap[i] = 0
		playerPairMapSessionVar = SessionVar(experimentSession=s, key=playerPairMapKey, value=pickle.dumps(playerPairMap))
		playerPairMapSessionVar.save()
	
	
	# Go through all of the remaining pairings and act as necessary.
	for pairIndex in range(playerPairMap[p.number], len(pairings)):

		pair = pairings[pairIndex]
		
		# check to see if participant is involved in pairing
		if ( checkPairForPlayer(pair, p.number) ):
			
			# Save pair index to the playerPairMap session var
			playerPairMap[p.number] = pairIndex + 1
			playerPairMapSessionVar.value = pickle.dumps(playerPairMap)
			playerPairMapSessionVar.save()
			
			# Get the name and identity of the other player in the pair
			opponentIdentity = getOpponentIdentity(pair, p.number, sid)
			opponentName = getOpponentName(pair, p.number, sid)
		
			# check if there is a decider involved
			if( checkForDecider(pair) ):
				# Get a list of possible components
				choices = []
				for choice in pair["choices"]:
					choices.append(Component.objects.get(id=choice))					
				# Make sure there is at least one component associated with the match.
				if(len(choices) < 1):
					raise AssertionError, "No exchange components were selected for this matcher. Edit the matcher component and add some."
				
				# If the current player is the decider...
				if ( checkPlayerIsDecider(pair, p.number) ):
									
					# Send to decider choice screen
					return render_to_response("matcher/matcher_decider.html", 
											{	'sid': sid, 
												'pname': pname,
												'parameters': parameters,
												'choices': choices,
												'opponentIdentity': opponentIdentity,
												'opponentName': opponentName
											}, 
										  	context_instance=RequestContext(request))
				else:
					# send to non decider screen
					return render_to_response("matcher/matcher_nonDecider.html", 
											{	'sid': sid, 
												'pname': pname,
												'parameters': parameters,
												'opponentIdentity': opponentIdentity,
												'opponentName': opponentName											
											}, 
										  	context_instance=RequestContext(request))
			else:
				# There is no decider, therefore direct the player to the first of the selected
				# decider choices. In theory, if there is no decider specified, there should be only one selected anyways.
				try:
					choiceID = pair["choices"][0]
				except:
					raise AssertionError, "No exchange components were selected for this matcher. Edit the matcher component and add some."
			
				# get the component object
				chosenComponent = Component.objects.get(id=choiceID)

				# Determine the kick off function for the component
				kickOffFunction = chosenComponent.componentType.kickoffFunction

				# redirect to the kickoff function of the component
				return HttpResponseRedirect('/' + kickOffFunction + '/?pname=' + pname + '&sid=' + sid+ '&opponentName=' + opponentName + '&exchangeComponentID=' + choiceID)		
	
	# After there are no more pairs to go through, go to the next component
	return HttpResponseRedirect('/session/drive/?pname=' + pname + '&sid=' + sid)


@login_required
def deciderSubmit(request):
	"""Handles the deciders exchange choice by writing the choice to the SessionVar table
		and starting the decider on the chosen component. """
	choiceID = request.POST.get("deciderChoice")
	sid = request.POST.get('sid')
	pname = request.POST.get('pname')
	opponentName = request.POST.get('opponentName')
	
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
	
	#Write the decider's choice to the log
	log_matcher(sid=sid,
				cid=c.id,
				componentIndex=p.currentComponent+1,
				deciderName=p.name,
				deciderPartner=opponentName,
				deciderChoice=choiceID
				).save()
	
	# redirect to the kickoff function of the chosen component
	return HttpResponseRedirect('/' + kickOffFunction + '/?pname=' + pname + '&sid=' + sid + '&opponentName=' + opponentName + '&exchangeComponentID=' + choiceID)		
	

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
	opponentName = request.GET.get('opponentName')
	
	# get the choice component object
	chosenComponent = Component.objects.get(id=choiceID)
	
	# Determine the kick off function for the chosen component
	kickOffFunction = chosenComponent.componentType.kickoffFunction
	
	# redirect to the kickoff function of the chosen component
	return HttpResponseRedirect('/' + kickOffFunction + '/?pname=' + pname + '&sid=' + sid + '&opponentName=' + opponentName + '&exchangeComponentID=' + choiceID)		
	

@login_required
def matcherEdit(request):
	"""Saves the contents of the matcher form"""
	comID = request.POST.get("comIM")
	
	# List of nex and rex components. The first item from this list is used if no component choices were selected.
	rexID = ComponentTypes.objects.get(componentType__exact="Reciprocal Exchange")
	nexID = ComponentTypes.objects.get(componentType__exact="Negotiated Exchange")
	componentList = Component.objects.filter(Q(componentType__exact=nexID.id)|Q(componentType__exact=rexID.id))
	
	if(len(componentList) == 0):
		response = "ERROR: You must create exchange components."
		return render_to_response('api.html', 
							  {'response': response}, 
							  context_instance=RequestContext(request))
	else:
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


def roundRobin(units, decider=0, rounds=1, choices=[], sets=None):
	""" Generates a schedule of "fair" pairings from a list of units """
	# modified from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/65200
	if len(units) % 2:
		units.append(None)
	count	 = len(units)
	sets	 = sets or (count - 1)
	half	 = count / 2
	schedule = []
	for turn in range(sets):
		for i in range(half):
			schedule.append({'p1': units[i], 'p2': units[count-i-1], 'decider':decider, 'rounds': rounds, 'choices':choices})
		units.insert(1, units.pop())
	return schedule

def checkPairForPlayer(pair, playerNumber):
	"""Accepts a pair and a player number. Returns true if player 
		is involved in the pairing and false if the player if not involved"""
	if( str(pair["p1"]) == str(playerNumber) or str(pair["p2"]) == str(playerNumber) ):
		return True
	else:
		return False

def checkForDecider(pair):
	"""Checks if the given pairing has a decider. Returns True if there is a decider
		False if there is not a decider"""
	if( int(pair["decider"]) > 0 ):
		return True
	else:
		return False
	
def checkPlayerIsDecider(pair, playerNumber):
	"""Checks if the given player is the decider in the given pair"""
	if( str(int(pair["decider"]) - 1) == str(playerNumber) ):
		return True
	else:
		return False

def getOpponentIdentity(pair, playerNumber, sid):
	"""Accepts a pair and a player number. Returns the identity Letter of the 
		other player in the pairing """
	p1 = str(pair["p1"])
	p2 = str(pair["p2"])
	playerNumber = str(playerNumber)
	
	if(playerNumber == p1):
		opponent = Participant.objects.get(experimentSession=sid, number=p2)
		return opponent.identityLetter
	elif(playerNumber == p2):
		opponent = Participant.objects.get(experimentSession=sid, number=p1)
		return opponent.identityLetter
	else:
		return False
	
def getOpponentName(pair, playerNumber, sid):
	"""Accepts a pair and a player number. Returns the name of the 
		other player in the pairing (e.g. 2007-07-30_000388 )"""
	p1 = str(pair["p1"])
	p2 = str(pair["p2"])
	playerNumber = str(playerNumber)
	
	if(playerNumber == p1):
		opponent = Participant.objects.get(experimentSession=sid, number=p2)
		return opponent.name
	elif(playerNumber == p2):
		opponent = Participant.objects.get(experimentSession=sid, number=p1)
		return opponent.name
	else:
		return False
	
	
	
	
	
	
	
	