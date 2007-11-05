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
def sessions(request):
	"""This page shows the 'Waiting for participants' and 'In progress' experiments."""
	expSessions = ExperimentSession.objects.all()
	experiments = Experiment.objects.all()
	return render_to_response('adminInterface/sessions.html', 
							  {'expSessions': expSessions,
							'experiments': experiments}, 
							  context_instance=RequestContext(request))
	

@login_required
def newSession(request):
	"""This creates a new experiment session"""
	expID = request.GET.get('id')
	expObject = Experiment.objects.get(id=expID)
	expSesStat = experimentSessionStatus.objects.get(statusText="Not Ready")
	e = ExperimentSession(experiment_id=expObject, status=expSesStat)
	e.save()
	sid = e.id
	
	return HttpResponseRedirect('/sessions/monitor/?sid=' + str(sid))

@login_required
def deleteSession(request):
	# TODO Don't delete, add a field to the model for inactive or something like that.
	"""This creates a new experiment session"""
	sid = request.GET.get('sid')
	expSes = ExperimentSession.objects.get(id=sid)
	expSes.delete()
	
	return HttpResponseRedirect('/sessions')


@login_required
def joinSession(request):
	"""Creates a participant object and add it to the session."""
	sid = request.GET.get('sid')
	expSes = ExperimentSession.objects.get(id=sid)
	
	# Get a list of all participants
	participantList = Participant.objects.filter(experimentSession=sid)
	
	# Get the min and max participants for the experiment
	minParticipants = expSes.experiment_id.minPlayers
	maxParticipants = expSes.experiment_id.maxPlayers

	if(len(participantList) < maxParticipants):	
		# Set participant's status
		partiStatus = participantStatus.objects.get(statusText="Ready")
		p = Participant(status=partiStatus, experimentSession=expSes, currentIteration=0, currentComponent=0)
	
		# Set the participant's player number
		participantsList = Participant.objects.filter(experimentSession__exact=sid)
		p.number = len(participantsList)
	
		# Set the participant's identity letter
		possibleIdentityLetters = ["T","D","K","M","F","G","R","L","S","W","H","Z"]
		p.identityLetter = possibleIdentityLetters[p.number]

		p.save()
	
		# Set participant's unique name
		p.name = p.dateCreated.strftime("%Y-%m-%d") + "_" + str(p.id).rjust(6,"0")
	
		p.save()
		
		if(len(participantList) + 1 >= minParticipants):
			expSes.status = experimentSessionStatus.objects.get(statusText="Ready")
			expSes.save()
		
		return HttpResponseRedirect('/session/wait/?pname=' + p.name + '&sid=' + sid)
	else:
		return HttpResponseRedirect('/sessions')
	
@login_required
def wait(request):
	"""Put the participant at a waiting screen."""
	return render_to_response('session/waiting.html', 
						  {'waitReason': "Waiting for experimenter to start...",
						   'partName': request.GET.get('pname'),
						   'sid': request.GET.get('sid')}, 
						  context_instance=RequestContext(request))


@login_required
def startSession(request):
	"""Initiates the experiment session"""	

	sid = request.GET.get('sid')
	
	# Get the session object
	sessionObj = ExperimentSession.objects.get(id=sid)
	
	if(sessionObj.status.statusText == "Ready"):
		# Get a list of the components
		componentsList = ExperimentComponents.objects.filter(experiment_id__exact=sessionObj.experiment_id.id)

		# Get a list of the participants
		participantsList = Participant.objects.filter(experimentSession__exact=sid)

		# Clean out the SessionVar table rows
		SessionVar.objects.filter(experimentSession=sessionObj).delete()
	
		# Make a sessionVariables object, pickle it, store it in SessionVar table
		# TODO Don't need current component and current iteration in sessionVaiables object
		sesVars = sessionVariables(componentsList, 0, 0, participantsList)
		sv = SessionVar(experimentSession=sessionObj, key="sesVars", value=pickle.dumps(sesVars))
		sv.save()
		
		# Change status to Running
		sesStatus = experimentSessionStatus.objects.get(statusText="Running")
		sessionObj.status = sesStatus
		sessionObj.save()
	
	return HttpResponseRedirect('/sessions/monitor/?sid=' + sid)

@login_required
def stopSession(request):
	"""Stops the session"""
	sid = request.GET.get('sid')
	expSes = ExperimentSession.objects.get(id=sid)
	
	# Delete sesVars
	SessionVar.objects.filter(experimentSession=expSes).delete()
	
	# Delete participants
	Participant.objects.filter(experimentSession__exact=sid).delete()
	
	# Change status from Running to canceled
	sesStatus = experimentSessionStatus.objects.get(statusText="Canceled")
	expSes.status = sesStatus
	expSes.save()
	
	return HttpResponseRedirect('/sessions/monitor/?sid=' + sid)

@login_required
def endSession(request):
	"""This function handles what happens when the experiment is over."""

	# TODO delete participant, if last participant, kill sesVars, add end date to session.
	return render_to_response('session/end.html', 
						  {'response': "Experiment finished"}, 
						  context_instance=RequestContext(request))


@login_required
def booted(request):
	"""Moves booted participants to a booted screen"""
	
	return render_to_response('session/booted.html', 
						  {'response': "booted"}, 
						  context_instance=RequestContext(request))
	

def driveSession(request):
	"""Moves participants along the session"""
	pname = request.GET.get('pname')
	sid = request.GET.get('sid')
	goback = request.GET.get('goback')	
	expSes = ExperimentSession.objects.get(id=sid)
	sesVars = loadSessionVars(sid)

	# Get the participant object
	try:
		p = Participant.objects.get(name=pname)
	except ObjectDoesNotExist:
		# TODO kill the session here in this case
		return HttpResponseRedirect("/session/booted/")
	
	# If goback is true, decrement the paticipants current component
	if(goback == "true"):
		p.currentComponent = p.currentComponent - 1
		p.currentIteration = 0
	
	# Quick check to make sure the session is still running.
	if(expSes.status.statusText != "Running"):
		return HttpResponseRedirect('/session/wait/?pname=' + pname + '&sid=' + sid)
	
	# Check if the participant has done all iterations of the current component
	if(sesVars.componentsList[int(p.currentComponent)].iterations == p.currentIteration):
		# if so, increment the current component and restart the iteration count
		p.currentComponent = p.currentComponent + 1
		p.currentIteration = 0
		
		# If that was the last component, redirect to the end screen
		if(len(sesVars.componentsList) == p.currentComponent):
			p.save()
			return HttpResponseRedirect('/session/end/?sid=' + sid)
	
	# increment the current component iteration count and save participant vars to the DB.
	p.currentIteration = p.currentIteration + 1
	p.save()
	
	# Determine the kick off function for the next component
	kickOffFunction = sesVars.componentsList[int(p.currentComponent)].component_id.componentType.kickoffFunction
	
	# redirect to the kickoff function of the next component
	return HttpResponseRedirect('/' + kickOffFunction + '/?pname=' + pname + '&sid=' + sid)

class sessionVariables:
	"""A data structure for session variables (not http sessions)"""	
	def __init__(self, componentsList, currentComponent, currentIteration, participantsList):
		self.componentsList = componentsList
		self.currentComponent = currentComponent
		self.currentIteration = currentIteration
		self.participantsList = participantsList
