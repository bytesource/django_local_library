"""locallibrary URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
]

# Use include() to add URLs from the catalog application
from django.conf.urls import include

urlpatterns += [
    url(r'^catalog/', include('catalog.urls')),
]

# Add URL maps to redirect the base URL to our application. 
# (/catalog/ is the only app we'll be using in this project.)
from django.views.generic import RedirectView

urlpatterns += [
    url(r'^$', RedirectView.as_view(url='/catalog/', permanent=True)),
]

# Add Django site authentication urls (for login, logout, password management)
urlpatterns += [
    # /localhost/accounts/
    # Views automatically provided by Django authentication middleware:
    # ^accounts/ ^login/$ [name='login']
    # ^accounts/ ^logout/$ [name='logout']
    # ^accounts/ ^password_change/$ [name='password_change']
    # ^accounts/ ^password_change/done/$ [name='password_change_done']
    # ^accounts/ ^password_reset/$ [name='password_reset']
    # ^accounts/ ^password_reset/done/$ [name='password_reset_done']
    # ^accounts/ ^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$ [name='password_reset_confirm']
    # ^accounts/ ^reset/done/$ [name='password_reset_complete']
    # NOTE: The views are also implicitly provided by Django.
    # NOTE: The templates are not provided by default, we need to add them ourselves!
    #       Templates need to be in a folder 'registration' on the template search path.
    # NOTE: r'^accounts/$' did not find accounts/login/
    url(r'^accounts/', include('django.contrib.auth.urls')),
]


# Use static() to add url mapping to serve static files during development (only)
from django.conf import settings 
from django.conf.urls.static import static 

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)