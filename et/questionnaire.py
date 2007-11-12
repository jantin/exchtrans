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
					questionText = "Click me to edit question text", 
					inputType = "textarea", 
					textAreaCols = 30, 
					textAreaRows = 5, 
					inputWidth = 30,
					questionType = "Free Text"
					):
		self.questionText = questionText
		self.inputType = inputType
		self.inputWidth = inputWidth
		self.textAreaCols = textAreaCols
		self.textAreaRows = textAreaRows
		self.questionType = questionType

class radioButtonQ(object):
	"""A Data structure for radio button questions"""
	def __init__(	self, 
					questionText = "Click me to edit question text", 
					questionChoices = ["Click to edit me", "Click to edit me"],
					questionType = "Radio Button"
					):
		self.questionText = questionText
		self.questionChoices = questionChoices
		self.questionType = questionType

class sliderQ(object):
	"""A Data structure for slider questions"""
	def __init__(	self, 	
					questionText = "Click me to edit question text", 
					leftScale = "Left Scale",
					rightScale = "Right Scale",
					sliderWidth = 400, 
					sliderStops = 50,
					questionType = "Slider"
					):
		self.questionText = questionText
		self.leftScale = leftScale				
		self.rightScale = rightScale
		self.sliderWidth = sliderWidth
		self.sliderStops = sliderStops
		self.questionType = questionType


class questionSet(object):
	"""A Data structure for questionnaire question sets"""
	def __init__(	self, 	
					questions = [],
					enableBack = False
					):
		self.questions = questions
		self.enableBack = enableBack


@login_required
def questionnaireDisplay(request):
	"""Displays the questionnaire"""
	sid = request.GET.get('sid')
	pname = request.GET.get('pname')
	
	p = Participant.objects.get(name=pname)
	cumulativePoints = p.cumulativePoints
	sesVars = loadSessionVars(sid)
	parameters = pickle.loads(sesVars.componentsList[int(p.currentComponent)].component_id.parameters)
	
	# get the current session object
	s = ExperimentSession.objects.get(id=sid)
	# get the current component object
	c = sesVars.componentsList[int(p.currentComponent)].component_id
	
	return render_to_response("questionnaire/questionnaire_display.html", 
							{	'sid': sid, 
								'pname': pname,
								'parameters': parameters,
								'cumulativePoints': cumulativePoints
							}, context_instance=RequestContext(request))


@login_required
def participantSubmit(request):
	"""Handles the submit of a questionnaire."""
	# Get the component
	sid = request.POST.get('sid')
	pname = request.POST.get('pname')
	
	p = Participant.objects.get(name=pname)
	sesVars = loadSessionVars(sid)
	parameters = pickle.loads(sesVars.componentsList[int(p.currentComponent)].component_id.parameters)
	
	# get the current component object
	c = sesVars.componentsList[int(p.currentComponent)].component_id
	
	qIndex = 1
	for q in parameters.questions:		
		log_questionnaire(	sid=sid,
							cid=c.id,
							componentIndex=p.currentComponent,
							participantName=p.name,
							questionType=q.questionType,
							questionText=q.questionText,
							questionResponse=request.POST.get('question_' + str(qIndex))
							).save()
		qIndex = qIndex + 1
	
	return HttpResponseRedirect('/session/drive/?sid='+sid+'&pname='+pname)

@login_required
def questionnaireAddQ(request):
	"""Adds a questionnaire question"""
	comId = request.POST.get('comId')
	qType = request.POST.get('qType')
	
	# Load the component from the DB
	component = Component.objects.get(id=comId)
	
	# Unpickle, update, and repickle the question set
	qSet = pickle.loads(component.parameters)
	exec("qSet.questions.append(" + qType + "())")	
	component.parameters = pickle.dumps(qSet)
	component.save()
	return HttpResponseRedirect('/components/edit/?id=' + comId)


@login_required
def questionnaireDeleteQ(request):
	"""Deletes a questionnaire question"""
	comId = request.GET.get('comId')
	qNum = int(request.GET.get('qid')) - 1
	
	# Load the component from the DB
	component = Component.objects.get(id=comId)
	
	# Unpickle, update, and repickle the question set
	qSet = pickle.loads(component.parameters)
	exec("qSet.questions.pop(" + str(qNum) + ")")	
	component.parameters = pickle.dumps(qSet)
	component.save()
	return HttpResponseRedirect('/components/edit/?id=' + comId)


@login_required
def addRadioChoice(request):
	"""Adds a radio button choice"""
	comId = request.GET.get('comId')
	qNum = int(request.GET.get('qid')) - 1
	
	# Load the component from the DB
	component = Component.objects.get(id=comId)
	
	# Unpickle, update, and repickle the question set
	qSet = pickle.loads(component.parameters)
	qSet.questions[qNum].questionChoices.append("Click to edit me")	
	component.parameters = pickle.dumps(qSet)
	component.save()
	return HttpResponseRedirect('/components/edit/?id=' + comId)


@login_required
def deleteRadioChoice(request):
	"""Adds a radio button choice"""
	comId = request.GET.get('comId')
	qNum = int(request.GET.get('qid')) - 1
	qc = int(request.GET.get('qc')) - 1
	
	# Load the component from the DB
	component = Component.objects.get(id=comId)
	
	# Unpickle, update, and repickle the question set
	qSet = pickle.loads(component.parameters)
	qSet.questions[qNum].questionChoices.pop(qc)	
	component.parameters = pickle.dumps(qSet)
	component.save()
	return HttpResponseRedirect('/components/edit/?id=' + comId)


@login_required
def editRadioChoice(request):
	"""Adds a radio button choice"""
	# element_id should be in the form of "<choice num>___<question num>___<Component ID>"
	elementList = request.POST.get('element_id').split("___")
	qc = int(elementList[0]) - 1
	qNum = int(elementList[1]) - 1
	comId = elementList[2]
	newValue = request.POST.get('update_value')
	
	# Load the component from the DB
	component = Component.objects.get(id=comId)
	
	# Unpickle, update, and repickle the question set
	qSet = pickle.loads(component.parameters)
	qSet.questions[qNum].questionChoices[qc] = newValue
	component.parameters = pickle.dumps(qSet)
	component.save()
	
	return render_to_response('api.html', 
						  {'response': newValue}, 
						  context_instance=RequestContext(request))


@login_required
def questionnaireEditParam(request):
	"""Handles in place editing on questionnaire editing screen"""
	# element_id should be in the form of "<Question Param Name>___<question num>___<Component ID>"
	elementList = request.POST.get('element_id').split("___")
	paramName = elementList[0]
	qNum = int(elementList[1]) - 1
	comId = elementList[2]
	newValue = request.POST.get('update_value')
	
	# Load the component from the DB
	component = Component.objects.get(id=comId)
	
	# Unpickle, update, and repickle the question set
	qSet = pickle.loads(component.parameters)
	exec("qSet.questions[qNum]." + paramName + " = newValue")	
	component.parameters = pickle.dumps(qSet)
	component.save()

	return render_to_response('api.html', 
						  {'response': newValue}, 
						  context_instance=RequestContext(request))


@login_required
def handleBackCheckbox(request):
	"""When users toggle back button checkbox, this updates the component"""
	# element_id should be in the form of "<choice num>___<question num>___<Component ID>"
	elementList = request.POST.get('elementId').split("___")
	comId = elementList[1]
	checked = request.POST.get('checked')
	
	# Load the component from the DB
	component = Component.objects.get(id=comId)
	
	# Unpickle, update, and repickle the question set
	qSet = pickle.loads(component.parameters)
	if(checked == "true"):
		qSet.enableBack = True
	else:
		qSet.enableBack = False
	component.parameters = pickle.dumps(qSet)
	component.save()
	
	return render_to_response('api.html', 
						  {'response': checked}, 
						  context_instance=RequestContext(request))
