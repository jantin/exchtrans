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
	"""This added a component to an experiment"""
	if (request.POST.get('addComponentID') != ""):
		# put the new component in last place
		orderCount = ExperimentComponents.objects.filter(experiment_id__exact=request.POST.get('expID')).count() + 1
	
		# insert the new component into the database
		ec = ExperimentComponents(experiment_id=Experiment.objects.get(id=request.POST.get('expID')),
								   component_id=Component.objects.get(id=request.POST.get('addComponentID')),
									order=orderCount)
		ec.save()
	
		# redirect back to the experiment editing page
	
	return HttpResponseRedirect('/editor/edit/?id=' + request.POST.get('expID'))

def newExperiment(request):
	"""This creates a new experiment"""
	if (request.POST.get('experimentName') != ""):

		# insert the new component into the database
		e = Experiment(name=request.POST.get('experimentName'),
					   description=request.POST.get('experimentDescription'),
						status=experimentStatus.objects.get(statusText='active'))
		e.save()
		
		# redirect back to the experiment editing page

	return HttpResponseRedirect('/editor/edit/?id=' + str(e.id))



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

@login_required
def experiment(request):
	"""This page allows you manage users"""
	return render_to_response('adminInterface/users.html', 
							  {'varName': 'sometext'}, 
							  context_instance=RequestContext(request))