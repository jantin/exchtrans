from django.http import HttpResponse
from django.shortcuts import render_to_response

def et2_login(request):
    html = "<html><body>In 3 hour(s), it will be OMG.</body></html>"
    return HttpResponse(html)

def et_login_form(request):
    return render_to_response('login.html', {'current_date': "now"})
