from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import (APITestCase, APIRequestFactory, force_authenticate,
                                 APIClient)
from dashboard.views import *
from dashboard.models import *


class CourseTest(APITestCase):

    fixtures = ['fixtures.json']

    def test_create_courses(self):
        data = {'name': 'test'}
        factory = APIRequestFactory()
        request = factory.post(reverse('course-list'), data=data)
        view = CourseViewSet.as_view({'post': 'create'})

        user = User.objects.get(is_superuser=False)
        force_authenticate(request, user=user)
        response = view(request)
        assert response.status_code == 403

        admin = User.objects.get(is_superuser=True)
        force_authenticate(request, user=admin)
        response = view(request)
        assert response.status_code == 201

    def test_edit_courses(self):
        course = Course.objects.all().first()
        data = {'name': 'test'}
        factory = APIRequestFactory()
        request = factory.patch(reverse('course-detail', args=(course.id, )), data=data)
        view = CourseViewSet.as_view({'patch': 'partial_update'})

        user = User.objects.get(is_superuser=False)
        force_authenticate(request, user=user)
        response = view(request, pk=course.id)
        assert response.status_code == 403

        admin = User.objects.get(is_superuser=True)
        force_authenticate(request, user=admin)
        response = view(request, pk=course.id)
        assert response.status_code == 200
        assert response.data['name'] == 'test'

        course.refresh_from_db()
        assert course.name == 'test'

    def test_delete_courses(self):
        course = Course.objects.all().first()
        factory = APIRequestFactory()
        request = factory.delete(reverse('course-detail', args=(course.id, )))
        view = CourseViewSet.as_view({'delete': 'destroy'})

        user = User.objects.get(is_superuser=False)
        force_authenticate(request, user=user)
        response = view(request, pk=course.id)
        assert response.status_code == 403

        admin = User.objects.get(is_superuser=True)
        force_authenticate(request, user=admin)
        response = view(request, pk=course.id)
        assert response.status_code == 204

    def test_add_user(self):
        course = Course.objects.all().first()
        user = User.objects.get(is_superuser=False)
        factory = APIRequestFactory()
        data = {'course_id': course.id, 'student_id': user.id}
        request = factory.post(reverse('course-add-user'), data=data)
        view = CourseViewSet.as_view({'post': 'add_user'})
        assert not user in course.students.all()

        force_authenticate(request, user=user)
        response = view(request)
        assert response.status_code == 403

        admin = User.objects.get(is_superuser=True)
        force_authenticate(request, user=admin)
        response = view(request)
        assert response.status_code == 200
        assert user in course.students.all()

    def test_remove_user(self):
        course = Course.objects.all().first()
        user = User.objects.get(is_superuser=False)
        factory = APIRequestFactory()
        data = {'course_id': course.id, 'student_id': user.id}
        request = factory.post(reverse('course-remove-user'), data=data)
        view = CourseViewSet.as_view({'post': 'remove_user'})
        course.students.add(user)
        assert user in course.students.all()

        force_authenticate(request, user=user)
        response = view(request)
        assert response.status_code == 403

        admin = User.objects.get(is_superuser=True)
        force_authenticate(request, user=admin)
        response = view(request)
        assert response.status_code == 200
        assert not user in course.students.all()

    def test_get_student_info(self):
        course = Course.objects.all().first()
        user = User.objects.get(is_superuser=False)
        factory = APIRequestFactory()
        request = factory.get(reverse('course-list'))
        view = CourseViewSet.as_view({'get': 'list'})
        course.students.add(user)
        assert user in course.students.all()

        force_authenticate(request, user=user)
        response = view(request)
        assert response.status_code == 403

        admin = User.objects.get(is_superuser=True)
        force_authenticate(request, user=admin)
        response = view(request)
        assert response.status_code == 200
        assert len(response.data) == Course.objects.all().count()
        assert response.data[0]['id'] == course.id
        assert len(response.data[0]['enrolled_students']) == 1
        assert len(response.data[0]['unregistered_students']) == 0
        assert response.data[0]['enrolled_students'][0]['id'] == user.id


class StudentTest(APITestCase):

    fixtures = ['fixtures.json']

    def test_enroll_courses(self):
        course = Course.objects.all().first()
        course.limit = 0
        course.save()
        user = User.objects.get(is_superuser=False)
        data = {'course': course.id}
        factory = APIRequestFactory()
        request = factory.post(reverse('user-enroll-course'), data=data, format='json')
        view = UserViewSet.as_view({'post': 'enroll_course'})

        force_authenticate(request, user=user)
        response = view(request)
        assert response.status_code == 422
        assert response.data['limit'][0] == 'Limit exceeded for the course'

        course.limit = 5
        course.save()
        request = factory.post(reverse('user-enroll-course'), data=data, format='json')
        force_authenticate(request, user=user)
        response = view(request)
        assert response.status_code == 200

    def test_cancel_courses(self):
        course = Course.objects.all().first()
        user = User.objects.get(is_superuser=False)
        data = {'course': course.id}
        factory = APIRequestFactory()
        request = factory.post(reverse('user-cancel-course'), data=data)
        view = UserViewSet.as_view({'post': 'cancel_course'})
        course.students.add(user)
        assert user in course.students.all()

        request = factory.post(reverse('user-cancel-course'), data=data)
        force_authenticate(request, user=user)
        response = view(request)
        assert response.status_code == 200
        assert not user in course.students.all()

    def test_courses_list(self):
        course = Course.objects.all().first()
        user = User.objects.get(is_superuser=False)
        factory = APIRequestFactory()
        request = factory.get(reverse('user-courses'))
        view = UserViewSet.as_view({'get': 'courses'})
        course.students.add(user)
        assert user in course.students.all()

        request = factory.get(reverse('user-courses'))
        force_authenticate(request, user=user)
        response = view(request)
        assert response.status_code == 200
        assert len(response.data['enrolled']) == 1
        assert len(response.data['available']) == 2
