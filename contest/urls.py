"""contest URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
# from django.views.generic import RedirectView
from . import settings
from .forms import BootstrapAuthenticationForm, BootstrapPasswordChangeForm

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/',
         auth_views.LoginView.as_view(
             authentication_form=BootstrapAuthenticationForm, redirect_authenticated_user=True),
         name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('change-password/',
         auth_views.PasswordChangeView.as_view(
             form_class=BootstrapPasswordChangeForm),
         name='password_change'),
    path('change-password/done/',
         auth_views.PasswordChangeDoneView.as_view(),
         name='password_change_done'),
    # path('accounts/', include('django.contrib.auth.urls')),
    path('', include('round.urls')),
    # path('round-two/', include('round.urls')),
    # path('', RedirectView.as_view(url='round-two/', permanent=True)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
