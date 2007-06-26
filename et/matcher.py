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

class matcherObj(object):
	"""A Data structure holding a matcher."""
	def __init__(	self, 
					pairings = [["0","1","0"],["2","3","0"]],
					randomPairing = True,
					randomComponentChoices = [],
					pair1ComponentChoices = [],
					pair2ComponentChoices = [], 
					randomRounds = "1",
					pair1rounds = "1",
					pair2rounds = "1"
				):
		self.pairings = pairings
		self.randomPairing = randomPairing
		self.randomComponentChoices = randomComponentChoices
		self.pair1ComponentChoices = pair1ComponentChoices
		self.pair2ComponentChoices = pair2ComponentChoices
		self.randomRounds = randomRounds
		self.pair1rounds = pair1rounds
		self.pair2rounds = pair2rounds
		'''
		If randomPairing is set to true, pairings, pair1rounds, and pair2rounds
		are ignored at runtime.
		
		The pairing stucture works as such:
		[[player 0, Player 1, Decider],...]
		
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
	
	return render_to_response("textPage/textPage_display.html", 
							{	'sid': sid, 
								'pname': pname,
								'parameters': parameters,
								'cumulativePoints': cumulativePoints
							}, 
						  	context_instance=RequestContext(request))

@login_required
def matcherEdit(request):
	"""Saves the contents of the matcher form"""
	comID = request.POST.get("comIM")
	
	# Slightly different form handling depending on the random pairing checkbox
	if(request.POST.get("randomPairingCheck") == "on"):
		componentParams = matcherObj(
									randomPairing = True,
									randomRounds = request.POST.get("randomRounds"),
									randomComponentChoices = request.POST.getlist("randomComponentChoices")
									)
	else:
		componentParams = matcherObj(
									randomPairing = False,
									pair1rounds = request.POST.get("pair1rounds"),
									pair2rounds = request.POST.get("pair2rounds"),
									pair1ComponentChoices = request.POST.getlist("pair1ComponentChoices"),
									pair2ComponentChoices = request.POST.getlist("pair2ComponentChoices"),
									pairings = [
													[
													request.POST.get("pair1p1"),
													request.POST.get("pair1p2"),
													request.POST.get("pair1decider")
													],
													[
													request.POST.get("pair2p1"),
													request.POST.get("pair2p1"),
													request.POST.get("pair2decider")
													]
												]
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
	count    = len(units)
	sets     = sets or (count - 1)
	half     = count / 2
	schedule = []
	for turn in range(sets):
		pairings = []
		for i in range(half):
			pairings.append([units[i], units[count-i-1], decider])
		units.insert(1, units.pop())
		schedule.append(pairings)
	return schedule