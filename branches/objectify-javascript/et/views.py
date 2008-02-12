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

def profile_redirect(request):
	"""The generic login view directs to a profile page. This redirects accounts/profile to somewhere else"""
	return HttpResponseRedirect('/sessions')


@login_required
def scratch(request):
	"""outputs scratch template for UI dev"""
	return render_to_response('scratch.html', 
						  {'name': "value"}, 
						  context_instance=RequestContext(request))

@login_required
def httpRPS(request):
	"""Make a DB query and return a result. Used for benchmarking"""
	startTime = time()
	sid = request.GET.get('sid')
	pname = request.GET.get('pname')
	
	# get the current Participant object
	p = Participant.objects.get(name=pname)
	cumulativePoints = p.cumulativePoints
	sesVars = loadSessionVars(sid)
	parameters = pickle.loads(sesVars.componentsList[int(p.currentComponent)].component_id.parameters)
	totalTime = time() - startTime
	response = {}
	response['time'] = totalTime
	jsonString = simplejson.dumps(response)
	return render_to_response('api.html', 
						  {'response': jsonString}, 
						  context_instance=RequestContext(request))

