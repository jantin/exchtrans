from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import Context, Template, RequestContext
from et.models import *

def sessionStatus(request):
	"""docstring for sessionStatus"""
	
	sid = request.GET.get('sid')
	ses = ExperimentSession.objects.get(id=sid)
	response = ses.status.statusText
	
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

