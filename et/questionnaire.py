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

class freeTextQ(object):
	"""A Data structure for freeText questions"""
	def __init__(	self, 	
					questionText = "Click to edit question text", 
					inputType = "textarea", 
					textAreaCols = 30, 
					textAreaRows = 5, 
					inputWidth = 30):
		self.questionText = questionText
		self.inputType = inputType
		self.inputWidth = inputWidth
		self.textAreaCols = textAreaCols
		self.textAreaRows = textAreaRows

class radioButtonQ(object):
	"""A Data structure for radio button questions"""
	def __init__(	self, 
					questionText = "Click to edit question text", 
					questionText = ["option1", "option2"]):
		self.questionText = questionText
		self.questionChoices = questionChoices

class sliderQ(object):
	"""A Data structure for slider questions"""
	def __init__(	self, 	
					questionText = "Click to edit question text", 
					sliderWidth = 400, 
					sliderStops = 20):
		self.questionText = questionText
		self.sliderWidth = sliderWidth
		self.sliderStops = sliderStops

@login_required
def questionnaireDisplay(request):
	"""Displays the questionnaire"""
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
def questionnaireEdit(request):
	"""Implements editing of questionnaire"""
		
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
