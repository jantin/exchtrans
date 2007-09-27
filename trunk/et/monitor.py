from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import Context, Template, RequestContext
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
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
	experimentComponents = Component.objects.filter(experimentcomponents__experiment_id__experimentsession__id=sid)
	
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
