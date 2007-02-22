from django.conf.urls.defaults import *
from django.contrib.auth.views import *
from exchtran.et.views import *

urlpatterns = patterns('',
    # Example:
	(r'^$', et_login_form),

    # Uncomment this for admin:
	#(r'^admin/', include('django.contrib.admin.urls')),
)
