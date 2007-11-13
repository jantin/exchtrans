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
	
	class Meta:
		ordering = ('name',)
		
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
	number = models.IntegerField()
	identityLetter = models.CharField(maxlength=1)
	
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
	
	class Meta:
		ordering = ('componentType',)
	
	class Admin:
		pass
	


class Component(models.Model):
	name = models.CharField(maxlength=255)
	description = models.TextField(null=True, default="")
	parameters = models.TextField(null=True)
	dateCreated = models.DateField(auto_now_add=True)
	dateModified = models.DateField(auto_now=True)
	componentType = models.ForeignKey(ComponentTypes)
	displayName = models.CharField(maxlength=255, null=True, default="Exchange Component")
	
	
	def __str__(self):
		return self.name
	
	class Meta:
		ordering = ('name',)
	
	class Admin:
		pass


class ExperimentComponents(models.Model):
	experiment_id = models.ForeignKey(Experiment)
	component_id = models.ForeignKey(Component)
	order = models.IntegerField()
	iterations = models.IntegerField()
	
	def __str__(self):
		return str(self.experiment_id) + "_" + str(self.component_id) + " " + str(self.order)
	
	class Meta:
		ordering = ('order',)
	
	class Admin:
		pass
	

class log_session(models.Model):
	sid = models.IntegerField()
	eid = models.IntegerField()
	experimentName = models.TextField()
	experimentDescription = models.TextField(null=True, default="")
	minPlayers = models.IntegerField()
	maxPlayers = models.IntegerField()
	playerCount = models.IntegerField()
	startTime = models.DateTimeField(auto_now_add=True)
	endTime = models.DateTimeField(null=True)
	exitMessage = models.TextField(null=True)
	timestamp = models.DateTimeField(auto_now_add=True)
	
	class Admin:
		pass

class log_components(models.Model):
	sid = models.IntegerField()
	cid = models.IntegerField()
	componentType = models.TextField()
	componentName = models.TextField()
	componentDescription = models.TextField(null=True, default="")
	componentParameters = models.TextField()
	componentIndex = models.IntegerField(null=True)
	timestamp = models.DateTimeField(auto_now_add=True)
	
	class Admin:
		pass

class log_participants(models.Model):
	sid = models.IntegerField()
	participantName = models.TextField()
	participantNumber = models.IntegerField()
	participantLetter = models.TextField()
	cumulativePoints = models.IntegerField(null=True)
	timestamp = models.DateTimeField(auto_now_add=True)
	
	class Admin:
		pass

class log_questionnaire(models.Model):
	sid = models.IntegerField()
	cid = models.IntegerField()
	componentIndex = models.IntegerField()
	participantName = models.TextField()
	questionType = models.TextField()
	questionText = models.TextField()
	questionResponse = models.TextField(null=True)
	timestamp = models.DateTimeField(auto_now_add=True)
	
	class Admin:
		pass

class log_nex(models.Model):
	sid = models.IntegerField()
	cid = models.IntegerField()
	componentIndex = models.IntegerField()
	roundIndex = models.IntegerField()
	offerIndex = models.IntegerField()
	participantName = models.TextField()
	participantPartner = models.TextField()
	startingX = models.IntegerField()
	startingY = models.IntegerField()
	initiatedOffer = models.TextField()
	xLoss = models.IntegerField()
	xGain = models.IntegerField()
	yLoss = models.IntegerField()
	yGain = models.IntegerField()
	xValue = models.IntegerField()
	yValue = models.IntegerField()
	outcome = models.TextField()
	nonBinding = models.TextField()
	followedThrough = models.TextField(null=True)
	pointChange = models.IntegerField(null=True)
	timestamp = models.DateTimeField(auto_now_add=True)
	
	class Admin:
		pass

class log_rex(models.Model):
	sid = models.IntegerField()
	cid = models.IntegerField()
	componentIndex = models.IntegerField()
	roundIndex = models.IntegerField()
	participantName = models.TextField()
	participantPartner = models.TextField()
	startingX = models.IntegerField()
	startingY = models.IntegerField()
	xLoss = models.IntegerField()
	xGain = models.IntegerField()
	yLoss = models.IntegerField()
	yGain = models.IntegerField()
	xValue = models.IntegerField()
	yValue = models.IntegerField()
	requiredGift = models.TextField()
	pointChange = models.IntegerField()
	timestamp = models.DateTimeField(auto_now_add=True)
	
	class Admin:
		pass

class log_matcher(models.Model):
	sid = models.IntegerField()
	cid = models.IntegerField()
	componentIndex = models.IntegerField()
	deciderName = models.TextField()
	deciderPartner = models.TextField()
	deciderChoice = models.TextField()
	timestamp = models.DateTimeField(auto_now_add=True)
	
	class Admin:
		pass

class SessionVar(models.Model):
	experimentSession = models.ForeignKey(ExperimentSession)
	key = models.TextField()
	value = models.TextField()
	unread = models.BooleanField(default=True)
	
	def __str__(self):
		return self.key + " (" + str(self.experimentSession) + ")"
	
	class Admin:
		pass
	
