from rest_framework import routers
from django.conf.urls import url

from .views import (CourseViewSet, UserViewSet, login_view,
                    index, logout_view, dashboard, register_view,
                    change_password_view)

router = routers.SimpleRouter()
router.register(r'api/courses', CourseViewSet)
router.register(r'api/users', UserViewSet)

urlpatterns = [
    url(r'^$', login_view),
    url('logout', logout_view),
    url('login', login_view),
    url('register', register_view),
    url('dashboard', dashboard),
    url('change-password', change_password_view),
]

urlpatterns += router.urls
