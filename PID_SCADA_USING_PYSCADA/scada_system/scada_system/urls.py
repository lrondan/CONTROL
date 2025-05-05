"""
URL configuration for scada_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
# scada_system/urls.py
from django.contrib import admin
from django.urls import path
from control_panel import views
from control_panel.views import historical_data
from control_panel.views import update_arduino_config, refresh_ports

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='dashboard'),
    path('system_data/', views.system_data, name='system_data'),
    path('send_command/<str:command>', views.send_command, name='send_command'),
    path('hisrtorical_data/', historical_data, name='historical_data'),
    path('update_config/', update_arduino_config, name='update_arduino_config'),
    path('refresh_ports/', refresh_ports, name='refresh_ports'),
]
