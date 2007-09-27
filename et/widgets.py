from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import Context, Template, RequestContext
from django.core.exceptions import ObjectDoesNotExist
from django.utils import simplejson
from models import *
from common import *
from views import *
import pickle
from time import time
import exchtran.settings
import os

# 
# Timer Widget
# 

class widgetTimerObj(object):
	"""A Data structure holding a timer widget object"""
	def __init__(	self, 
					mins = 3,
					secs = 30
				):
		self.mins = mins
		self.secs = secs
		
@login_required
def timerDisplay(request):
	"""Displays the timer widget"""
		
	return render_to_response("widgets/timer_display.html", 
							{	
							}, 
						  	context_instance=RequestContext(request))

@login_required
def timerEdit(request):
	"""Saves the contents of the timer widget component form"""
		
	comID = request.POST.get("comIM")
		
	componentParams = widgetTimerObj(
									mins = request.POST.get("mins"),
									secs = request.POST.get("secs")
									)

	c = Component.objects.get(id=comID)
	c.name = request.POST.get("componentName")
	c.description = request.POST.get("componentDescription")
	c.displayName = request.POST.get("displayName")
	c.parameters = pickle.dumps(componentParams)
	c.save()
	
	response = "Component Saved"
	return render_to_response('api.html', 
						  {'response': response}, 
						  context_instance=RequestContext(request))

# 
# Image Widget
# 
class widgetImageObj(object):
	"""A Data structure holding an image widget object"""
	def __init__(	self, 
					fileName = None,
					filePath = None,
					fileType = None,
					webPath = None
				):
		self.fileName = fileName
		self.filePath = filePath
		self.fileType = fileType
		self.webPath = webPath

@login_required
def imageDisplay(request):
	"""Displays the image widget"""
		
	return render_to_response("widgets/timer_display.html", 
							{	
							}, 
						  	context_instance=RequestContext(request))


@login_required
def imageEdit(request):
	"""Saves the contents of the image widget component form"""
	
	comID = request.POST.get("comIM")
	c = Component.objects.get(id=comID)
	
	# Handle file upload
	try:
		fileName = request.FILES['imageUpload']['filename']
		filePath = exchtran.settings.UPLOAD_DIR + request.FILES['imageUpload']['filename']
		fileType = request.FILES['imageUpload']['content-type']
		webPath = "/site_media/uploads/" + fileName
	except:
		pass
	else:
		
		# Check for previously uploaded images, delete if found
		oldParameters = pickle.loads(c.parameters)
		if(oldParameters.filePath != None):
			os.remove(oldParameters.filePath)
		
		validFileTypes = ['.png', '.jpg', '.gif']
		if (filePath[-4:] in validFileTypes):
			f = open(filePath,"w")
			f.write(request.FILES['imageUpload']['content'])
			f.close()
		
		componentParams = widgetImageObj(
									fileName = fileName,
									filePath = filePath,
									fileType = fileType,
									webPath = webPath
									)
		c.parameters = pickle.dumps(componentParams)
	
	# Handle the name and description fields
	c.name = request.POST.get("componentName")
	c.description = request.POST.get("componentDescription")
	c.displayName = request.POST.get("displayName")
	c.save()
	
	return HttpResponseRedirect('/components/edit/?id=' + comID)

# 
# Bank Widget
# 
class widgetBankObj(object):
	"""A Data structure holding an bank widget object"""
	def __init__(	self, 
					topLabel = ""
				):
		self.topLabel = topLabel

@login_required
def bankDisplay(request):
	"""Displays the bank widget"""
		
	return render_to_response("widgets/timer_display.html", 
							{	
							}, 
						  	context_instance=RequestContext(request))


@login_required
def bankEdit(request):
	"""Saves the contents of the bank widget component form"""
	
	comID = request.POST.get("comIM")
		
	componentParams = widgetBankObj(
									topLabel = request.POST.get("topLabel")
									)

	c = Component.objects.get(id=comID)
	c.name = request.POST.get("componentName")
	c.description = request.POST.get("componentDescription")
	c.displayName = request.POST.get("displayName")
	c.parameters = pickle.dumps(componentParams)
	c.save()
	
	response = "Component Saved"
	return render_to_response('api.html', 
						  {'response': response}, 
						  context_instance=RequestContext(request))


