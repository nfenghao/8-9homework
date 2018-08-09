import json
from django.shortcuts import HttpResponse
from django.http import JsonResponse

from rest_framework.views import APIView
from rest_framework.viewsets import ViewSetMixin

from rest_framework.response import Response
from rest_framework.versioning import URLPathVersioning
from rest_framework.pagination import PageNumberPagination

from api import models
from api.serializers.course import CourseSerializer, CourseModelSerializer
from api.utils.response import BaseResponse
import redis

conn = redis.Redis(host='192.168.11.30', port=6379)


class CoursesView(ViewSetMixin, APIView):

    def list(self, request, *args, **kwargs):
        # response = {'code':1000,'data':None,'error':None}
        ret = BaseResponse()
        try:
            # 从数据库获取数据
            queryset = models.Course.objects.all()

            # 分页
            page = PageNumberPagination()
            course_list = page.paginate_queryset(queryset, request, self)

            # 分页之后的结果执行序列化
            ser = CourseModelSerializer(instance=course_list, many=True)

            ret.data = ser.data
        except Exception as e:
            ret.code = 500
            ret.error = '获取数据失败'

        return Response(ret.dict)

    def create(self, request, *args, **kwargs):
        """
        增加
        :param request:
        :param args:
        :param kwargs:
        :return:
        """

    def retrieve(self, request, pk, *args, **kwargs):
        response = {'code': 1000, 'data': None, 'error': None}
        try:
            course = models.Course.objects.get(id=pk)
            ser = CourseModelSerializer(instance=course)
            response['data'] = ser.data
        except Exception as e:
            response['code'] = 500
            response['error'] = '获取数据失败'
        return Response(response)

    def update(self, request, pk, *args, **kwargs):
        """
        修改
        :param request:
        :param pk:
        :param args:
        :param kwargs:
        :return:
        """
        pass

    def destroy(self, request, pk, *args, **kwargs):
        """
        删除
        :param request:
        :param pk:
        :param args:
        :param kwargs:
        :return:
        """


class ShoppingCarView(ViewSetMixin, APIView):
    def list(self, request, *args, **kwargs):
        conn.hset('xx', 'k1', '冯昊')
        conn.hset('xx', 'k2', '冯日天')
        n1 = conn.hget('xx', 'k1').decode('utf-8')
        n2 = conn.hget('xx', 'k2').decode('utf-8')
        print(n1, n2)
        return Response('...')

    def create(self, request, *args, **kwargs):
        """
        加入购物车
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        """
        1. 接受用户选中的课程ID和价格策略ID
        2. 判断合法性
            - 课程是否存在？
            - 价格策略是否合法？
        3. 把商品和价格策略信息放入购物车 SHOPPING_CAR

        注意：用户ID=1
        """
        return Response({'code': 11111})
