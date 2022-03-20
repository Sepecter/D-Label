from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from rest_framework import exceptions
from server import models
from django.http import JsonResponse
import base64
from io import BytesIO
import zipfile
import json
from django.http import FileResponse


def md5(user):
    import hashlib
    import time
    ctime = str(time.time())
    m = hashlib.md5(bytes(user, encoding='utf-8'))
    m.update(bytes(ctime, encoding='utf-8'))
    return m.hexdigest()


class Authtication(object):

    def authenticate(self, request):
        if request.method == 'GET':
            return
        token = request.data.get('token')
        token_obj = models.User_Info.objects.filter(token=token).first()
        if not token_obj:
            raise exceptions.AuthenticationFailed('token失效')
        return (token_obj, token)

    def authenticate_header(self, request):
        pass


class Login(APIView):

    def post(self, request):
        ret = {}
        email = request.POST.get('username')
        password = request.POST.get('password')
        if not email or not password:
            ret['code'] = 404
            ret['msg'] = '请求参数错误'
            return JsonResponse(ret)
        user = models.User_Info.objects.filter(email=email, password=password).first()
        if not user:
            ret['code'] = 404
            ret['msg'] = '用户名或密码错误'
            return JsonResponse(ret)
        token = md5(user.email)
        user.token = token
        user.save()
        ret['code'] = 200
        ret['token'] = token
        return JsonResponse(ret)


class Register(APIView):

    def post(self, request):
        ret = {}
        email = request.POST.get('username')
        password = request.POST.get('password')
        if not email or not password:
            ret['code'] = 404
            ret['msg'] = '请求参数错误'
            return JsonResponse(ret)
        user = models.User_Info.objects.filter(email=email).first()
        if user:
            ret['code'] = 404
            ret['msg'] = '用户已注册'
            return JsonResponse(ret)
        token = md5(email)
        models.User_Info.objects.create(email=email, password=password, token=token)
        ret['code'] = 200
        ret['token'] = token
        return JsonResponse(ret)


class Collection(APIView):

    def get(self, request):
        ret = {}
        collection_id = request.GET.get('collection_id')
        collection = models.Collection_Info.objects.filter(id=collection_id).first()
        photo = models.Photo_Info.objects.filter(collection=collection)
        label = models.Label_Info.objects.filter(belonging=collection)
        photo_id_list = []
        class_detail = []
        for i in photo:
            photo_id_list.append(i.id)
        for i in label:
            class_detail.append((i.label_name, i.number))
        ret['code'] = 200
        ret['name'] = collection.name
        ret['photo_number'] = collection.photo_number
        ret['photo_id_list'] = photo_id_list
        ret['class_number'] = collection.class_number
        ret['class_detail'] = class_detail
        return JsonResponse(ret)

    authentication_classes = [Authtication, ]

    def post(self, request):
        ret = {}
        user = request.user
        name = request.POST.get('name')
        collection = models.Collection_Info.objects.create(name=name, owner_id=user.id)
        ret['code'] = 200
        ret['collection_id'] = collection.id
        return JsonResponse(ret)

    def delete(self, request):
        ret = {}
        user = request.user
        collection_id = request.POST.get('collection_id')
        models.Collection_Info.objects.filter(id=collection_id).delete()
        ret['code'] = 200
        return JsonResponse(ret)


class Photo(APIView):

    def get(self, request):
        ret = {}
        photo_id = request.GET.get('photo_id')
        object = models.Photo_Info.objects.filter(id=photo_id).first()
        if not object:
            ret['code'] = 404
            return JsonResponse(ret)
        ret['photo'] = object.photo
        ret['label'] = object.label
        ret['code'] = 200
        return JsonResponse(ret)

    authentication_classes = [Authtication, ]

    def post(self, request):
        ret = {}
        collection_id = request.POST.get('collection_id')
        image = request.POST.get('image')
        label = request.POST.get('label')
        label_object = models.Label_Info.objects.filter(belonging_id=collection_id, label_name=label).first()
        if not label_object:
            label_object = models.Label_Info.objects.create(label_name=label, belonging_id=collection_id)
            label_object.belonging.class_number = label_object.belonging.class_number + 1
            label_object.belonging.save()
        label_object.number = label_object.number + 1
        label_object.save()
        collection_object = label_object.belonging
        collection_object.photo_number = collection_object.photo_number + 1
        collection_object.save()
        photo = models.Photo_Info.objects.create(photo=image, label_id=label_object.id, collection_id=collection_id)
        ret['code'] = 200
        ret['photo_id'] = photo.id
        return JsonResponse(ret)

    def delete(self, request):
        ret = {}
        photo_id = request.POST.get('photo_id')
        photo = models.Photo_Info.objects.filter(id=photo_id).first()
        if not photo:
            ret['code'] = 404
            return JsonResponse(ret)
        label = photo.label
        label.number = label.number - 1
        if label.number == 0:
            label.belonging.class_number = label.belonging.class_number - 1
            label.belonging.save()
            label.delete()
        photo.collection.photo_number = photo.collection.photo_number - 1
        photo.collection.save()
        photo.delete()
        ret['code'] = 200
        return JsonResponse(ret)


class User_Info(APIView):

    def get(self, request):
        ret = {}
        token = request.GET.get('token')
        user = models.User_Info.objects.filter(token=token).first()
        collection = models.Collection_Info.objects.filter(owner_id=user.id)
        collection_id_list = []
        for i in collection:
            collection_id_list.append(i.id)
        ret['code'] = 200
        ret['collection_id_list'] = collection_id_list
        return JsonResponse(ret)


class Download(APIView):

    def get(self, request):
        collection_id = request.GET.get('collection_id')

        labels = models.Label_Info.objects.filter(belonging_id=collection_id)
        categories_data = {}
        for i in labels:
            images = models.Photo_Info.objects.filter(label_id=i.id)
            Arrlist = []
            for j in images:
                Arrlist.append(j.id)
            categories_data[i.label_name] = Arrlist
        images = models.Photo_Info.objects.filter(collection_id=collection_id)
        download_io = BytesIO()
        with zipfile.ZipFile('images.zip', 'w', zipfile.ZIP_DEFLATED) as zip_fp:
            for i in images:
                img_data = base64.b64decode(i.photo)
                with zip_fp.open('image_%d.jpg' % i.id, 'w') as f:
                    f.write(img_data)
            with zip_fp.open('categories.json', 'w') as f:
                f.write(json.dumps(categories_data).encode("utf-8"))
        download_io.seek(0)
        return FileResponse(download_io, as_attachment=True, filename="images.zip")
