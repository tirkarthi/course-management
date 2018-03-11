from django.contrib import admin
from django.conf.urls import include, url

import dashboard

urlpatterns = [
    url('', include('dashboard.urls'))
]
