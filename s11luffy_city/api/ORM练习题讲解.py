from django.shortcuts import render,HttpResponse
# from django.views import View
from rest_framework.viewsets import ModelViewSet
from api import serializers as app01_serializers
import json
from rest_framework.views import APIView
from api.models import CourseCategory,CourseSubCategory,\
    DegreeCourse,Teacher,Scholarship,Course,CourseDetail,OftenAskedQuestion,\
    CourseOutline,CourseChapter,CourseSection,CourseSection,CourseSection
class Courses(ModelViewSet):
    queryset=Course.objects.all()
    serializer_class =app01_serializers.Course_serializers


