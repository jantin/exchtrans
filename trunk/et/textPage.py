from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import Context, Template, RequestContext
from django.core.exceptions import ObjectDoesNotExist
from et.models import *
from et.common import *
from et.views import *
import pickle
from time import time

class textPageObj(object):
	"""A Data structure holding a textPage"""
	def __init__(self, heading, body, buttonLabel, template):
		self.heading = heading
		self.body = body
		self.buttonLabel = buttonLabel
		self.template = template
		self.timestamp = time()


@login_required
def textPageDisplay(request):
	"""Displays the text page"""
	sid = request.GET.get('sid')
	pname = request.GET.get('pname')
	
	p = Participant.objects.get(name=pname)
	cumulativePoints = p.cumulativePoints
	sesVars = loadSessionVars(sid)
	parameters = pickle.loads(sesVars.componentsList[int(p.currentComponent)].component_id.parameters)
	
	if (parameters.template == "Full"):
		template = "textPage/textPage_displayFull.html"
	else:
		template = "textPage/textPage_displayActionArea.html"
	
	return render_to_response(template, 
							{	'sid': sid, 
								'pname': pname,
								'parameters': parameters,
								'cumulativePoints': cumulativePoints
							}, 
						  	context_instance=RequestContext(request))

@login_required
def textPageEdit(request):
	"""Saves the contents of the text page form"""
		
	comID = request.POST.get("comIM")
	
	componentParams = textPageObj(	request.POST.get("heading"),
									request.POST.get("body"),
									request.POST.get("buttonLabel"),
									request.POST.get("template")
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

