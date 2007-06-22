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

class nexObj(object):
	"""A Data structure holding a negotiated exchange object"""
	def __init__(	self, 
					p1x = 20, 
					p1y = 10, 
					p1xReplenish = 20,
					p1yReplenish = 10,
					p1Clearing = "End of round",
					p2x = 20, 
					p2y = 10,
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
		self.p1xReplenish = p1xReplenish
		self.p1yReplenish = p1yReplenish
		self.p1Clearing = p1Clearing
		self.p2x = p2x
		self.p2y = p2y
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
	
	return render_to_response("nex/nex_display.html", 
							{	'sid': sid, 
								'pname': pname,
								'parameters': parameters,
								'cumulativePoints': cumulativePoints
							}, 
						  	context_instance=RequestContext(request))

@login_required
def nexEdit(request):
	"""Saves the contents of the negotiated exchange component form"""
		
	comID = request.POST.get("comIM")
	
	if(request.POST.get("enableBack") == "on"):
		enableBack = True
	else:
		enableBack = False
	
	componentParams = textPageObj(	request.POST.get("heading"),
									request.POST.get("body"),
									request.POST.get("buttonLabel"),
									enableBack
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

