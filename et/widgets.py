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


# 
# Timer Widget
# 

class widgetTimerObj(object):
	"""A Data structure holding a timer widget object"""
	def __init__(	self, 
					something = None
				):
		self.something = something
		
@login_required
def timerDisplay(request):
	"""Displays the timer widget"""
		
	return render_to_response("widgets/timer_display.html", 
							{	
							}, 
						  	context_instance=RequestContext(request))

@login_required
def timerEdit(request):
	"""Saves the contents of the timer widget component form"""
		
	comID = request.POST.get("comIM")
		
	componentParams = widgetTimerObj(
								something = None
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

# 
# Image Widget
# 
class widgetImageObj(object):
	"""A Data structure holding an image widget object"""
	def __init__(	self, 
					something = None
				):
		self.something = something

@login_required
def imageDisplay(request):
	"""Displays the timer widget"""
		
	return render_to_response("widgets/timer_display.html", 
							{	
							}, 
						  	context_instance=RequestContext(request))


@login_required
def imageEdit(request):
	"""Saves the contents of the image widget component form"""
		
	comID = request.POST.get("comIM")
		
	componentParams = widgetTimerObj(
								something = None
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