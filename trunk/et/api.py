from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import Context, Template, RequestContext
from django.core.exceptions import ObjectDoesNotExist
from models import *
from common import *

def sessionStatus(request):
	"""Wait screen pings this function to determine when it should move the participant forward"""
	
	pname = request.GET.get('pname')
	sid = request.GET.get('sid')
	sesObj = ExperimentSession.objects.get(id=sid)
	response = sesObj.status.statusText
	
	# See if the participant still exists in the DB
	# If not, respond with "Booted"
	try:
		pObj = Participant.objects.get(name=pname)
	except ObjectDoesNotExist:
		response = "Booted"
	
	
	return render_to_response('api.html', 
							  {'response': response}, 
							  context_instance=RequestContext(request))

def rex_toolTipImages(request):
	"""Responds with content for the requested tooltip"""
	
	image = request.GET.get('image')
	response = "<img src='/site_media/images/rex_offer.png' />"

	
	return render_to_response('api.html', 
							  {'response': response}, 
							  context_instance=RequestContext(request))

def updateField(request):
	"""updates a field in the database. Used with inline editing javascript"""
	# element_id should be in the form of "<fieldName>___<experiment ID>"
	elementList = request.POST.get('element_id').split("___")
	fieldName = elementList[0]
	expID = elementList[1]
	newValue = request.POST.get('update_value')
	
	expObj = Experiment.objects.get(id=expID)
	exec("expObj." + fieldName + " = newValue")
	expObj.save()
	
	return render_to_response('api.html', 
							  { 'response': newValue}, 
							  context_instance=RequestContext(request))
	


def saveComponentChanges(request):
	"""receives the order of components from the experiment edit page and updates the database"""
	# has param is in the form of "componentsList[]=component___7&componentsList[]=component___8"
	components = request.POST.get('hash').split("&")
	counter = 1
	for c in components:
		c = c.split("=")
		c = c[1].split("___")
		expCompID = c[1]
		expCompObj = ExperimentComponents.objects.get(id=expCompID)
		expCompObj.order = counter
		expCompObj.save()
		counter = counter + 1
		
	
	
	return render_to_response('api.html', 
							  { 'response': "OK"}, 
							  context_instance=RequestContext(request))

























