from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import Context, Template, RequestContext
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.utils import simplejson
from models import *
from common import *
import pickle
from time import time


@login_required
def monitor(request):
	"""This page allows the experimenter to monitor the progress of a running experiment."""
	# fetch all sessions for sessions drop down
	expSessions = ExperimentSession.objects.all()
	
	
	sid = request.GET.get('sid')
	monitorSession = ExperimentSession.objects.get(id=sid)
	participants = Participant.objects.filter(experimentSession=sid)
	experimentComponents = Component.objects.filter(experimentcomponents__experiment_id__experimentsession__id=sid).extra(select={'order_col': "et_component__experimentcomponents.order"}).order_by('order_col')
	
	if(monitorSession.status.statusText == "Running"):
		running = True
	else:
		running = False
	
	if(len(participants) > 0):
		noParticipants = False
	else:
		noParticipants = True
	
	return render_to_response('adminInterface/monitor.html', 
							{	'expSessions': expSessions, 
								'monitorSession':monitorSession,
								'participants':participants,
								'noParticipants':noParticipants,
								'running':running,
								'experimentComponents':experimentComponents
							},
							  context_instance=RequestContext(request))

@login_required
def updatePollProcess(request):
	"""This process returns the status of all the participants and the experiement."""
	sid = request.GET.get('sid')
	response = {}
	
	# Get the participants
	participants = Participant.objects.filter(experimentSession=sid).order_by('number')
	
	# Get the experiment status
	experimentStatus = ExperimentSession.objects.get(id=sid).status.statusText
	response['experimentStatus'] = experimentStatus

	participantList = []
	# For each participant...
	for p in participants:
		pObject = {}
		pObject['name'] = p.name
		pObject['id'] = p.id
		pObject['identityLetter'] = p.identityLetter
		pObject['number'] = p.number
		pObject['currentComponent'] = p.currentComponent
		pObject['cumulativePoints'] = p.cumulativePoints
		participantList.append(pObject)	
	response['participants'] = participantList
	
	jsonString = simplejson.dumps(response)
	return render_to_response('api.html', 
						  {'response': jsonString}, 
						  context_instance=RequestContext(request))


@login_required
def bootParticipant(request):
	"""Boots participants by deleting them"""
	pid = request.GET.get('pid')
	sid = request.GET.get('sid')
	
	p = Participant.objects.get(id=pid)
	p.delete()
		
	# Get a list of all participants
	participantList = Participant.objects.filter(experimentSession=sid)
	
	# Get the min and max participants for the experiment
	s = ExperimentSession.objects.get(id=sid)
	minParticipants = s.experiment_id.minPlayers
	
	if(len(participantList) < minParticipants):
		s.status = experimentSessionStatus.objects.get(statusText="Not Ready")
		s.save()
	
	return HttpResponseRedirect(request.META['HTTP_REFERER'])











