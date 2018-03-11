from rest_framework import serializers

from django.contrib.auth.models import User

from .models import Course


class UserInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "email")


class UserSerializer(serializers.ModelSerializer):

    courses = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "email", "courses")
        depth = 1

    def get_courses(self, obj):
        return CourseUserSerializer(obj.course_set.all(), many=True).data


class CourseUserSerializer(serializers.ModelSerializer):

    availability = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ("id", "limit", "name", "availability")

    def get_availability(self, instance):
        return instance.students.all().count() < instance.limit


class CourseAdminSerializer(serializers.ModelSerializer):

    availability = serializers.SerializerMethodField()
    enrolled_students = serializers.SerializerMethodField()
    unregistered_students = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ("id", "limit", "name", "availability",
                  "enrolled_students", "unregistered_students")

    def get_enrolled_students(self, instance):
        return UserInfoSerializer(instance.students.all(), many=True).data

    def get_unregistered_students(self, instance):
        user_ids = list(instance.students.all().values_list('id', flat=True))
        unregistered_students = User.objects.exclude(
            id__in=user_ids).exclude(is_superuser=True)
        return UserInfoSerializer(unregistered_students, many=True).data

    def get_availability(self, instance):
        return instance.students.all().count() < instance.limit


class ChangeCourseSerializer(serializers.Serializer):

    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())

    def validate(self, data):
        course = data["course"]
        if not course.students.all().count() < course.limit:
            raise serializers.ValidationError(
                {"limit": "Limit exceeded for the course"})

        return data


class ChangePasswordSerializer(serializers.Serializer):

    password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError(
                {"password": "Passwords don't match"})

        return data
