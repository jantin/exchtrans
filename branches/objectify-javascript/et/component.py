from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import Context, Template, RequestContext
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from models import *
from common import *
from textPage import *
from questionnaire import *
from rex import *
from matcher import *
from nex import *
from widgets import *
from monitor import *
import pickle
from time import time
from time import sleep

@login_required
def components(request):
	"""This page lists all components in the system."""
	components = Component.objects.all()
	componentTypes = ComponentTypes.objects.all()
	return render_to_response('adminInterface/components.html', 
							  {	'components': components, 
								'componentTypes': componentTypes}, 
							  context_instance=RequestContext(request))

@login_required
def componentEdit(request):
	"""This page displays a single component for editing"""
	comID = request.GET.get('id')
	component = Component.objects.get(id=comID)
	parameters = pickle.loads(component.parameters)
	
	# List of nex and rex components used for matcher module
	rexID = ComponentTypes.objects.get(componentType__exact="Reciprocal Exchange")
	nexID = ComponentTypes.objects.get(componentType__exact="Negotiated Exchange")
	componentList = Component.objects.filter(Q(componentType__exact=nexID.id)|Q(componentType__exact=rexID.id))
	
	# Get a list of widgets that could potentially be added
	widgetList = Component.objects.filter(componentType__componentType__startswith='Widget:')
	
	
	return render_to_response(	component.componentType.editTemplate, 
								{'component': component,
								 'parameters': parameters,
								 'componentList': componentList,
								 'widgetList': widgetList
								}, 
						  		context_instance=RequestContext(request))


# TODO duplicate component
# TODO export component
# TODO load component

@login_required
def componentCreate(request):
	"""This function creates a new component instance"""
	# Get information from POST vars
	componentName = request.POST.get('componentName')
	componentType = request.POST.get('componentType')
	
	# Get component type object
	componentType = ComponentTypes.objects.get(id=componentType)
	
	# Set default parameters
	if (componentType.componentType == "Reciprocal Exchange"):
		componentParams = rexObj()
	
	if (componentType.componentType == "Questionnaire"):
		componentParams = questionSet()
	
	if (componentType.componentType == "Text Page"):
		componentParams = textPageObj()
	
	if (componentType.componentType == "Matcher"):
		componentParams = matcherObj()

	if (componentType.componentType == "Negotiated Exchange"):
		componentParams = nexObj()	

	if (componentType.componentType == "Widget: Timer"):
		componentParams = widgetTimerObj()	
		
	if (componentType.componentType == "Widget: Image"):
		componentParams = widgetImageObj()	
	
	if (componentType.componentType == "Widget: Bank"):
		componentParams = widgetBankObj()	
	
	
	# Add component to the database
	c = Component(	name = componentName,
					parameters = pickle.dumps(componentParams),
					componentType = componentType
					)
	c.save()
	
	return HttpResponseRedirect('/components/edit/?id=' + str(c.id))

@login_required
def componentDelete(request):
	# TODO Don't delete, add a field to the model for inactive or something like that.
	"""This deletes a component"""
	cid = request.GET.get('cid')
	comp = Component.objects.get(id=cid)
	comp.delete()
	
	return HttpResponseRedirect('/components')
