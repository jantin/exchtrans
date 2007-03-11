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
	
	def __str__(self):
		return self.name
	
	class Admin:
		pass
	

class ExperimentSession(models.Model):
	experiment_id = models.ForeignKey(Experiment)
	status = models.ForeignKey(experimentSessionStatus)
	dateStarted = models.DateField(auto_now_add=True)
	dateEnded = models.DateField()
	
	def __str__(self):
		return str(self.experiment_id) + "_" + str(self.dateStarted) + "_" + str(self.ExperimentSession_id)
	
	class Admin:
		pass
	

class Participant(models.Model):
	name = models.CharField(maxlength=100)
	status = models.ForeignKey(participantStatus)
	experimentSession = models.ForeignKey(ExperimentSession)
	dateCreated = models.DateField(auto_now_add=True)

	def __str__(self):
		return self.name

	class Admin:
		pass
	

class Component(models.Model):
	name = models.CharField(maxlength=255)
	description = models.TextField()
	parameters = models.TextField()
	
	def __str__(self):
		return self.name
	
	class Admin:
		pass
	

class ExperimentComponents(models.Model):
	experiment_id = models.ForeignKey(Experiment)
	component_id = models.ForeignKey(Component)
	order = models.IntegerField()
	
	def __str__(self):
		return str(self.experiment_id) + "_" + str(self.component_id) + " " + str(self.order)
	
	class Meta:
		ordering = ('order',)
	
	class Admin:
		pass
	
