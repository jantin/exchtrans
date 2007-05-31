from django import template
register = template.Library()
import os

@register.tag
def svn_version(parser, token):
	f = os.popen('svnversion')
	version = f.read()[0:-1] # trim off the newline
	f.close()
	return svn_version_node(version)

class svn_version_node(template.Node):
	def __init__(self, version_string):
		self.version_string = version_string
	def render(self, context):
		return self.version_string