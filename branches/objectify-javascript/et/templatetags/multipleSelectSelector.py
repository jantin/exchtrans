from django import template
from django.template import resolve_variable
register = template.Library()

@register.tag
def multipleSelectSelector(parser, token):
	'''Accepts a list of selected IDs and the current ID. If the current ID is in the 
		list of selected IDs, the selected="selected" text is output. Used to highlight
		previously selected options in multiple select elements'''
	tagName, selectedIDs, currentID = token.split_contents()
	return multipleSelectSelector_node(selectedIDs,currentID)

class multipleSelectSelector_node(template.Node):
	def __init__(self, selectedIDs,currentID):
		self.selectedIDs = selectedIDs
		self.currentID = currentID
	def render(self, context):
		selectedIDs = resolve_variable(self.selectedIDs, context)
		currentID = resolve_variable(self.currentID, context)
		
		if str(currentID) in selectedIDs:
			return 'selected="selected"'
		else:
			return ""