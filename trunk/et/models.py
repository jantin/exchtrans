from django.db import models

class Status(models.Model):
    statusText = models.CharField(maxlength=100)

class Experiment(models.Model):
	eid = models.AutoField(primary_key=True)
	name = models.CharField(maxlength=100)
	description = models.TextField()
	status = models.ForeignKey(Status)
	dateCreated = models.DateField('auto_now_add')
	dateModified = models.DateField('auto_now')

class Trial(models.Model):
	pass
	
class Publisher(models.Model):
    name = models.CharField(maxlength=30)
    address = models.CharField(maxlength=50)
    city = models.CharField(maxlength=60)
    state_province = models.CharField(maxlength=30)
    country = models.CharField(maxlength=50)
    website = models.URLField()

class Author(models.Model):
    salutation = models.CharField(maxlength=10)
    first_name = models.CharField(maxlength=30)
    last_name = models.CharField(maxlength=40)
    email = models.EmailField()

class Book(models.Model):
    title = models.CharField(maxlength=100)
    authors = models.ManyToManyField(Author)
    publisher = models.ForeignKey(Publisher)
    publication_date = models.DateField()
