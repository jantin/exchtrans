from django.db import models

class experimentSessionStatus(models.Model):
	statusText = models.CharField(maxlength=100)
	
	def __str__(self):
		return self.statusText
	
	class Admin:
		pass
	

class experimentStatus(models.Model):
	statusText = models.CharField(maxlength=100)
	
	def __str__(self):
		return self.statusText
	
	class Admin:
		pass
	

class participantStatus(models.Model):
	statusText = models.CharField(maxlength=100)
	
	def __str__(self):
		return self.statusText
	
	class Admin:
		pass
	

class Experiment(models.Model):
	name = models.CharField(maxlength=100)
	description = models.TextField()
	status = models.ForeignKey(experimentStatus)
	dateCreated = models.DateField(auto_now_add=True)
	dateModified = models.DateField(auto_now=True)
	minPlayers = models.IntegerField()
	maxPlayers = models.IntegerField()
	
	def __str__(self):
		return self.name
	
	class Admin:
		pass
	

class ExperimentSession(models.Model):
	experiment_id = models.ForeignKey(Experiment)
	status = models.ForeignKey(experimentSessionStatus)
	dateStarted = models.DateField(auto_now_add=True)
	dateEnded = models.DateField(null=True, blank=True)
	
	def __str__(self):
		return "Session id: " + str(self.id) + " (" + str(self.experiment_id) + ")" 
	
	class Admin:
		pass
	

class Participant(models.Model):
	name = models.CharField(maxlength=100, null=True)
	status = models.ForeignKey(participantStatus)
	experimentSession = models.ForeignKey(ExperimentSession)
	dateCreated = models.DateField(auto_now_add=True)
	currentComponent = models.IntegerField(null=True)
	currentIteration = models.IntegerField(null=True)
	cumulativePoints = models.IntegerField(null=True,default=0)
	
	def __str__(self):
		return self.name

	class Admin:
		pass
	

class ComponentTypes(models.Model):
	componentType = models.CharField(maxlength=255)
	kickoffFunction = models.CharField(maxlength=255)
	editTemplate = models.CharField(maxlength=255)
	kickoffTemplate = models.CharField(maxlength=255)
	
	def __str__(self):
		return self.componentType
	
	class Admin:
		pass
	


class Component(models.Model):
	name = models.CharField(maxlength=255)
	description = models.TextField(null=True)
	parameters = models.TextField(null=True)
	dateCreated = models.DateField(auto_now_add=True)
	dateModified = models.DateField(auto_now=True)
	componentType = models.ForeignKey(ComponentTypes)
	
	
	def __str__(self):
		return self.name
	
	class Admin:
		pass


class ExperimentComponents(models.Model):
	experiment_id = models.ForeignKey(Experiment)
	component_id = models.ForeignKey(Component)
	order = models.IntegerField()
	iterations = models.IntegerField()
	
	# add parameters here, remove from Component
	def __str__(self):
		return str(self.experiment_id) + "_" + str(self.component_id) + " " + str(self.order)
	
	class Meta:
		ordering = ('order',)
	
	class Admin:
		pass
	

class SessionLog(models.Model):
	participant = models.ForeignKey(Participant)
	experimentComponent = models.ForeignKey(ExperimentComponents)
	timestamp = models.DateField(auto_now_add=True)
	message = models.TextField()
	
	def __str__(self):
		return self.message
	
	class Admin:
		pass
	

class SessionVar(models.Model):
	experimentSession = models.ForeignKey(ExperimentSession)
	key = models.TextField()
	value = models.TextField()
	
	def __str__(self):
		return self.key + " (" + str(self.experimentSession) + ")"
	
	class Admin:
		pass
	
