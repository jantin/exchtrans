from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import Context, Template, RequestContext
from django.core.exceptions import ObjectDoesNotExist
from models import *
import pickle
from time import time

def loadSessionVars(sid):
	"""Returns unpickled SesVars"""
	expSes = ExperimentSession.objects.get(id=sid)
	sv = SessionVar.objects.get(experimentSession=expSes,key="sesVars")
	sesVars = pickle.loads(sv.value)
	return sesVars