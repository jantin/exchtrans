from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import Context, Template, RequestContext
from et.models import *

def profile_redirect(request):
	"""The generic login view directs to a profile page. This redirects accounts/profile to somewhere else"""
	return HttpResponseRedirect('/dashboard')

@login_required
def dashboard(request):
	"""This page shows the 'Waiting for participants' and 'In progress' experiments."""
	expSessions = ExperimentSession.objects.all()
	return render_to_response('adminInterface/dashboard.html', 
							  {'expSessions': expSessions}, 
							  context_instance=RequestContext(request))

@login_required
def monitor(request):
	"""This page allows the experimenter to monitor the progress of a running experiment."""
	expSessions = ExperimentSession.objects.all()
	sesID = request.GET.get('id')
	monitorSession = ExperimentSession.objects.get(id=sesID)
	participants = Participant.objects.filter(experimentSession__exact=sesID)
	return render_to_response('adminInterface/monitor.html', 
							  {'expSessions': expSessions, 
							   'monitorSession':monitorSession,
							   'participants':participants},
							  context_instance=RequestContext(request))

@login_required
def editor(request):
	"""The editor allow you to create new experiments and edit existing ones."""
	experimentList = Experiment.objects.values('name', 'id')
	
	return render_to_response('adminInterface/editor.html', 
							  { 'experimentList': experimentList }, 
							  context_instance=RequestContext(request))

def edit(request):
	"""This view allows you to edit an existing experiment"""
	expID = request.GET.get('id')
	expDetails = Experiment.objects.get(id=expID)
	componentList = Component.objects.values()
	experimentComponentsList = ExperimentComponents.objects.filter(experiment_id__exact=expID)	

	return render_to_response('adminInterface/edit.html', 
							  { 'expID': expID, 
								'componentList': componentList, 
								'experimentComponentsList': experimentComponentsList,
								'expDetails': expDetails }, 
							  context_instance=RequestContext(request))

def addComponent(request):
	"""This adds a component to an experiment"""
	if (request.POST.get('addComponentID') != ""):
		# put the new component in last place
		orderCount = ExperimentComponents.objects.filter(experiment_id__exact=request.POST.get('expID')).count() + 1
	
		# insert the new component into the database
		ec = ExperimentComponents(experiment_id=Experiment.objects.get(id=request.POST.get('expID')),
								   component_id=Component.objects.get(id=request.POST.get('addComponentID')),
									order=orderCount)
		ec.save()
	
		# redirect back to the experiment editing page
	
	return HttpResponseRedirect('/experiments/edit/?id=' + request.POST.get('expID'))

def newExperiment(request):
	"""This creates a new experiment"""
	if (request.POST.get('experimentName') != ""):

		# insert the new component into the database
		e = Experiment(name=request.POST.get('experimentName'),
					   description=request.POST.get('experimentDescription'),
						status=experimentStatus.objects.get(statusText='active'))
		e.save()
		
		# redirect back to the experiment editing page

	return HttpResponseRedirect('/experiments/edit/?id=' + str(e.id))

def newSession(request):
	"""This creates a new experiment session"""
	expID = request.GET.get('id')
	expObject = Experiment.objects.get(id=expID)
	expSesStat = experimentSessionStatus.objects.get(statusText="Not Ready")
	e = ExperimentSession(experiment_id=expObject, status=expSesStat)
	e.save()
	
	return HttpResponseRedirect('/experiments/view/?id=' + str(expID))

def deleteSession(request):
	"""This creates a new experiment session"""
	expID = request.GET.get('id')
	expObject = Experiment.objects.get(id=expID)
	expSesStat = experimentSessionStatus.objects.get(statusText="Not Ready")
	e = ExperimentSession(experiment_id=expObject, status=expSesStat)
	e.save()
	
	return HttpResponseRedirect('/experiments/view/?id=' + str(expID))



@login_required
def experiments(request):
	"""This page lists all experiments in the system."""
	experiments = Experiment.objects.all()
	return render_to_response('adminInterface/archive.html', 
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
def joinSession(request):
	"""Creates a participant object and add it to the session."""
	sesID = request.GET.get('id')
	partiStatus = experimentSessionStatus.objects.get(statusText="ready")
	expSes = ExperimentSession.objects.get(id=sesID)
	p = Participant(status=partiStatus, experimentSession=expSes)
	p.save()
	p.name = p.dateCreated.strftime("%Y-%m-%d") + "_" + str(p.id).rjust(4,"0")
	p.save()
	return HttpResponseRedirect('/session/wait/?pname=' + p.name)
	

def wait(request):
	"""Put the participant at a waiting screen."""
	return render_to_response('session/waiting.html', 
						  {'waitReason': "Waiting for experimenter to start",
						   'partName': request.GET.get('pname')}, 
						  context_instance=RequestContext(request))

def startSession(request):
	"""Initiates the experiment session"""
	return HttpResponseRedirect('/dashboard')
	
class rex:
	"""This class drives reciprocal exchange"""
	def __init__(self, participants, params):
		self.participants = participants
		self.params = params
	
	