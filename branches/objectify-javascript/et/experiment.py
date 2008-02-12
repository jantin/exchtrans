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
def edit(request):
	"""This view allows you to edit an existing experiment"""
	expID = request.GET.get('id')
	expDetails = Experiment.objects.get(id=expID)
	componentList = Component.objects.filter(componentType__componentType__in=['Matcher','Text Page','Questionnaire'])
	experimentComponentsList = ExperimentComponents.objects.filter(experiment_id__exact=expID)	

	return render_to_response('adminInterface/edit.html', 
							  { 'expID': expID, 
								'componentList': componentList, 
								'experimentComponentsList': experimentComponentsList,
								'expDetails': expDetails }, 
							  context_instance=RequestContext(request))

@login_required
def experiments(request):
	"""This page lists all experiments in the system."""
	experiments = Experiment.objects.all()
	return render_to_response('adminInterface/experiments.html', 
							  {'experiments': experiments}, 
							  context_instance=RequestContext(request))


@login_required
def viewExperiment(request):
	"""This page lists all experiments in the system."""
	expID = request.GET.get('id')
	experimentComponentsList = ExperimentComponents.objects.filter(experiment_id__exact=expID)
	experimentSessions = ExperimentSession.objects.filter(experiment_id__exact=expID)
	experiment = Experiment.objects.get(id=expID)
	return render_to_response('adminInterface/experimentView.html', 
							  {'experiment': experiment,
							   'experimentComponentsList': experimentComponentsList,
							   'experimentSessions': experimentSessions
							   }, 
							  context_instance=RequestContext(request))
	
@login_required
def addComponent(request):
	"""This adds a component to an experiment"""
	if (request.POST.get('addComponentID') != ""):
		# put the new component in last place
		orderCount = ExperimentComponents.objects.filter(experiment_id__exact=request.POST.get('expID')).count() + 1
	
		# insert the new component into the database
		ec = ExperimentComponents(experiment_id=Experiment.objects.get(id=request.POST.get('expID')),
								   component_id=Component.objects.get(id=request.POST.get('addComponentID')),
								iterations=1,
									order=orderCount)
		ec.save()
	
		# redirect back to the experiment editing page
	
	return HttpResponseRedirect('/experiments/edit/?id=' + request.POST.get('expID'))

@login_required
def removeComponent(request):
	# TODO convert this to a POST operation
	"""This removes a component from an experiment"""
	if (request.GET.get('removeComponentID') != ""):
		
		expID = request.GET.get('expID')
		expCompID = request.GET.get('expCompID');
			
		# insert the new component into the database
		ec = ExperimentComponents.objects.get(id=expCompID)
		ec.delete()
	
		# redirect back to the experiment editing page
	return HttpResponseRedirect('/experiments/edit/?id=' + expID)

@login_required
def newExperiment(request):
	"""This creates a new experiment"""
	if (request.POST.get('experimentName') != ""):

		# insert the new component into the database
		e = Experiment	(	name = request.POST.get('experimentName'),
					   		description = "",
							status = experimentStatus.objects.get(statusText='Waiting for participants'),
							minPlayers = 4,
							maxPlayers = 4
						)
		e.save()
		
		# redirect back to the experiment editing page

	return HttpResponseRedirect('/experiments/edit/?id=' + str(e.id))

@login_required
def experimentDelete(request):
	# TODO Don't delete, add a field to the model for inactive or something like that.
	"""This creates a new experiment session"""
	eid = request.GET.get('eid')
	e = Experiment.objects.get(id=eid)
	e.delete()
	
	return HttpResponseRedirect('/experiments')
