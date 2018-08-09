import json
import redis
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSetMixin
from rest_framework.response import Response

from api import models
from api.utils.response import BaseResponse

conn = redis.Redis(host='192.168.11.136', port=6379)

USER_ID = 1


class ShoppingCarView(ViewSetMixin, APIView):
    # parser_classes = [JSONParser,]
    # parser_classes = [JSONParser,FormParser,]
    def list(self, request, *args, **kwargs):
        # conn.hset('xx', 'k1', '冯昊')
        # conn.hset('xx', 'k2', '冯xx')
        # n1 = conn.hget('xx', 'k1').decode('utf-8')
        # n2 = conn.hget('xx', 'k2').decode('utf-8')
        # print(n1, n2)
        # return Response('...')
        '''
        查看购物车消息
        :param request:
        :param args:
        :param kwargs:
        :return:
        '''
        ret = {'code': 10000, 'data': None, 'error': None}
        try:
            shopping_car_course_list = []
            # pattern = 'shopping_car_%s_*'%(USER_ID,)
            pattern = settings.LUFFY_SHOPPING_CAR % (USER_ID, '*')
            user_key_list = conn.keys(pattern)
            for key in user_key_list:
                temp = {
                    'id': conn.hget(key, 'id').decode('utf-8'),
                    'name': conn.hget(key, 'name').decode('utf-8'),
                    'img': conn.hget(key, 'img').decode('utf-8'),
                    'default_price_id': conn.hget(key, 'default_price_id').decode('utf-8'),
                    'price_policy_dict': json.loads(conn.hget(key, 'price_policy_dict').decode('utf-8'))
                }
                shopping_car_course_list.append(temp)
                ret['data'] = shopping_car_course_list
        except Exception as e:
            ret['code'] = 10005
            ret['error'] = '获取购物车数据失败'

        return Response(ret)

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
        # 1.接收用户选中的课程id和价格策略id
        '''
        问题:
        1.如果让你编写一个api程序,你需要先做什么?
            -了解业务需求
            -统一数据传输格式
            -表结构设计
            -程序开发
        2.django restful framework 的解析器的parser_class的作用?
        根据请求中的content-type请求头的值,选择指定解析对请求体中的数据进行解析
        比如说:
            请求头含有content-type:application/json,则内部使用的是jsonParser,
            jsonparser可以自动去请求体request,body中
            获取请求数据,然后进行字节转换字符串,json,loads反序列化
        3.支持多个解析器,(一般只是jsonparser就可以)
        
        '''
        course_id = request.data.get('courseid')
        policy_id = request.data.get('polocyid')
        # 2.判断合法性,
        # -课程是否存在
        # -价格策略是否合法

        # 首先证明课程是否存在
        course = models.Course.objects.filter(id=course_id).first()
        if not course:
            return Response({'code': 10001, 'error': '课程不存在'})
        # 价格策略是否合法
        price_policy_queryset = course.price_policy.all()
        price_policy_dict = {}
        for item in price_policy_queryset:
            temp = {
                'id': item.id,
                'price': item.price,
                'valid_period': item.valid_period,
                'valid_period_display': item.get_valid_period_display()

            }
            price_policy_dict[item.id] = temp
            if policy_id not in price_policy_dict:
                return Response({'code': 10002, 'error': '不要乱操作'})

            pattern = settings.LUFFY_SHOPPING_CAR % (USER_ID, course_id)
            keys = conn.keys(pattern)
            if keys and len(keys) >= 1000:
                return Response({'code': 10009, 'error': '购物车东西很多,先去结算再去购买'})
            # key = 'shopping_car_%S_%s%(USER_id,course_id)
            key = settings.LUFFY_SHOPPING_CAR % (USER_ID, course_id)
            conn.hset(key, 'id', course_id)
            conn.hset(key, 'name', course.name)
            conn.hset(key, 'img', course.course_img)
            conn.hset(key, 'default_price_id', policy_id)
            conn.hset(key, 'price_policy_dict', json.dumps(price_policy_dict))
            conn.expire(key, 20 * 60)
            return Response({'code': 10000, 'data': '购买成功'})

    def destory(self, request, *args, **kwargs):
        '''
        删除购物车中的某个课程
        :param request:
        :param args:
        :param kwargs:
        :return:
        '''
        response = BaseResponse()
        try:
            courseid = request.GET.get('courseid')
            # key = 'shopping_car_%s_%s' %(USER_ID,courseid)
            key = settings.LUFFY_SHOPPING_CAR % (USER_ID, courseid)
            conn.delete(key)
            response.data = '删除成功'
        except Exception as e:
            response.code = 10006
            response.error = '删除失败'
            return Response(response.dict)

    def update(self, request, *args, **kwargs):
        '''
        修改用户的价格策略
        :param request:
        :param args:
        :param kwargs:
        :return:
        '''
        '''
        1.获取课程id,要修改的价格策略id
        2.校验合法性(去redis中)
        '''
        response = BaseResponse()
        try:
            course_id = request.data.get('courseid')
            policy_id = str(request.data.get('policyid')) if request.data.get('policyid') else None
            # key = 'shopping_car_%s_%s' %(USER_ID,course_id,)
            key = settings.LUFFY_SHOPPING_CAR % (USER_ID, course_id)
            if not conn.exists(key):
                response.code = 10007
                response.error = '课程不存在'
                return Response(response.dict)
            price_policy_dict = json.loads(conn.hget(key, 'price_policy_dict').decode('utf-8'))
            if policy_id not in price_policy_dict:
                response.code = 10008
                response.error = '价格策略不存在'
                return Response(response.dict)
            conn.hset(key, 'default_price_id', policy_id)
            conn.expire(key, 20 * 60)
            response.data = '修改成功'
        except Exception as  e:
            response.code = 10009
            response.error = '修改失败'
        return Response(response.dict)
