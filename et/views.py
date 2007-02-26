from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import Context, Template, RequestContext

def profile_redirect(request):
	"""The generic login view directs to a profile page. This redirects accounts/profile to somewhere else"""
	return HttpResponseRedirect('/dashboard')

@login_required
def dashboard(request):
	"""This page shows the active experiments."""
	return render_to_response('adminInterface/dashboard.html', 
							  {'varName': 'sometext'}, 
							  context_instance=RequestContext(request))

@login_required
def monitor(request):
	"""This page allows the experimenter to monitor the progress of a running experiment."""
	return render_to_response('adminInterface/monitor.html', 
							  {'varName': 'sometext'}, 
							  context_instance=RequestContext(request))

@login_required
def editor(request):
	"""The editor allow you to create new experiments and edit existing ones."""
	return render_to_response('adminInterface/editor.html', 
							  {'varName': 'sometext'}, 
							  context_instance=RequestContext(request))

@login_required
def archive(request):
	"""This page lists all experiments in the system."""
	return render_to_response('adminInterface/archive.html', 
							  {'varName': 'sometext'}, 
							  context_instance=RequestContext(request))

@login_required
def users(request):
	"""This page allows you manage users"""
	return render_to_response('adminInterface/users.html', 
							  {'varName': 'sometext'}, 
							  context_instance=RequestContext(request))
