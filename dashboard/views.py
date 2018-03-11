from rest_framework import viewsets, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.decorators import api_view, detail_route, list_route
from rest_framework.response import Response

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, F

from .permissions import IsAdminUserOrReadOnly
from .serializers import (CourseUserSerializer, CourseAdminSerializer, UserSerializer,
                          ChangeCourseSerializer, ChangePasswordSerializer)
from .models import Course


def index(request):
    return render(request, "index.html")


def logout_view(request):
    logout(request)
    return redirect('/login')


def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/dashboard')
        else:
            return render(request, "index.html",
                          context={"form_error": "Invalid username or password"})
    else:
        return render(request, "index.html")


def register_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        user = User.objects.filter(username=username).exists()
        if not first_name:
            return render(request, "register.html",
                          context={"form_error": "First name is required"})
        elif not last_name:
            return render(request, "register.html",
                          context={"form_error": "Last name is required"})
        elif not password:
            return render(request, "register.html",
                          context={"form_error": "A password is required"})
        elif user:
            return render(request, "register.html",
                          context={"form_error": "Username already exists"})
        else:
            user = User.objects.create(username=username, first_name=first_name,
                                       last_name=last_name)
            user.set_password(password)
            user.save()
            return redirect('/login')
    else:
        return render(request, "register.html")


@login_required
def change_password_view(request):
    user = request.user
    if request.method == "POST":
        current_password = request.POST.get('current_password')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        user = authenticate(request, username=user.username,
                            password=current_password)
        if not user:
            return render(request, "change_password.html",
                          context={"form_error": "Invalid current password"})
        elif not password or password != confirm_password:
            return render(request, "change_password.html",
                          context={"form_error": "Passwords don't match"})
        else:
            user.set_password(password)
            user.save()
            return redirect('/dashboard')
    else:
        return render(request, "change_password.html")


@login_required
def dashboard(request):
    user = request.user
    if user.is_superuser:
        return render(request, "admin.html")
    else:
        return render(request, "dashboard.html")


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


class CourseViewSet(viewsets.ModelViewSet):

    authentication_classes = (CsrfExemptSessionAuthentication, )
    permission_classes = (IsAdminUser, )
    queryset = Course.objects.all()
    serializer_class = CourseAdminSerializer

    @list_route(methods=['post'])
    def add_user(self, request, *args, **kwargs):
        user = request.user
        course = Course.objects.get(id=request.data['course_id'])
        student = User.objects.get(id=request.data['student_id'])
        course.students.add(student)
        return Response({}, status=status.HTTP_200_OK)

    @list_route(methods=['post'])
    def remove_user(self, request, *args, **kwargs):
        user = request.user
        course = Course.objects.get(id=request.data['course_id'])
        student = User.objects.get(id=request.data['student_id'])
        course.students.remove(student)
        return Response({}, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ViewSet):

    authentication_classes = (CsrfExemptSessionAuthentication, )
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ['courses', 'enroll_course', 'cancel_course']:
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [IsAdminUser]
        return super(self.__class__, self).get_permissions()

    @list_route(methods=['get'])
    def courses(self, request, *args, **kwargs):
        user = request.user
        enrolled = Course.objects.filter(students=user)
        available = Course.objects.annotate(student_count=Count('students'))\
                                  .exclude(students=user)\
                                  .exclude(student_count__gte=F('limit'))
        response = {'enrolled': CourseUserSerializer(enrolled, many=True).data,
                    'available': CourseUserSerializer(available, many=True).data}
        return Response(response, status=status.HTTP_200_OK)

    @list_route(methods=['post'])
    def enroll_course(self, request, *args, **kwargs):
        user = request.user
        serializer = ChangeCourseSerializer(data=request.data)
        if serializer.is_valid():
            course = serializer.validated_data['course']
            course.students.add(user)
            course_serializer = CourseUserSerializer(course)
            return Response(course_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    @list_route(methods=['post'])
    def cancel_course(self, request, *args, **kwargs):
        user = request.user
        serializer = ChangeCourseSerializer(data=request.data)
        if serializer.is_valid():
            course = serializer.validated_data['course']
            course.students.remove(user)
            course_serializer = CourseUserSerializer(course)
            return Response(course_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
