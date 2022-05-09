from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from rest_framework import exceptions
from server import models
from django.http import JsonResponse
import base64
from torchvision import transforms
from server.model_v2 import MobileNetV2
import torch
from PIL import Image
import os
import json
from datetime import datetime
from io import BytesIO
import zipfile
from django.http import FileResponse
from django.http import HttpResponse


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
        return token_obj, token

    def authenticate_header(self, request):
        pass


class Login(APIView):

    def post(self, request):
        ret = {}
        email = request.POST.get('username')
        password = request.POST.get('password')
        user_type = request.POST.get('user_type')
        if not email or not password:
            ret['code'] = 404
            ret['msg'] = '请求参数错误'
            return JsonResponse(ret)
        user = models.User_Info.objects.filter(email=email, password=password, user_type=int(user_type)).first()
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
        user_type = request.POST.get('user_type')
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
        models.User_Info.objects.create(email=email, password=password, token=token, user_type=int(user_type))
        ret['code'] = 200
        ret['token'] = token
        return JsonResponse(ret)


class Collection(APIView):

    def get(self, request):
        ret = {}
        collection_id = request.GET.get('collection_id')
        image_code = request.GET.get('image_code')
        token = request.GET.get('token')
        user = models.User_Info.objects.filter(token=token).first()
        collection = models.Collection_Info.objects.filter(id=collection_id).first()
        if (not collection.owner.filter(token=token)) & (collection.permission != 0):
            ret['code'] = 404
        photo = models.Photo_Info.objects.filter(collection=collection)
        label = models.Label_Info.objects.filter(belonging=collection)
        photo_id_list = []
        class_detail = []
        for i in photo:
            photo_id_list.append(i.id)
        for i in label:
            first_photo = models.Photo_Info.objects.filter(label_id=i.id).first()
            dic = {
                'class_name': i.label_name,
                'photo_number': i.number,
                'image': first_photo.photo
            }
            class_detail.append(dic)
        ret['code'] = 200
        ret['name'] = collection.name
        ret['description'] = collection.description
        ret['created_time'] = collection.created_time
        ret['photo_number'] = collection.photo_number
        ret['photo_id_list'] = photo_id_list
        ret['class_number'] = collection.class_number
        ret['class_detail'] = class_detail
        if image_code == '1':
            image = []
            for i in photo:
                dic = {
                    'id': i.id,
                    'image': i.photo,
                    'created_time': i.created_time,
                    'label': i.label.label_name,
                    'sub_label': i.sub_label,
                    'coordinate1': i.coordinate1,
                    'coordinate2' : i.coordinate2
                }
                image.append(dic)
            ret['image'] = image
        return JsonResponse(ret)

    authentication_classes = [Authtication, ]

    def post(self, request):
        ret = {}
        user = request.user
        name = request.POST.get('name')
        description = request.POST.get('description')
        collection_type = request.POST.get('collection_type')
        permission = request.POST.get('permission')
        collection = models.Collection_Info.objects.create(name=name, owner_id=user.id,
                                                           description=description, collection_type=collection_type,
                                                           permission=permission, created_time=str(datetime.now()), )
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
        obj = models.Photo_Info.objects.filter(id=photo_id).first()
        if not obj:
            ret['code'] = 404
            return JsonResponse(ret)
        ret['code'] = 200
        ret['photo'] = obj.photo
        ret['label'] = obj.label.label_name
        ret['sub_label'] = obj.sub_label
        ret['created_time'] = obj.created_time
        ret['coordinate1'] = obj.coordinate1
        ret['coordinate2'] = obj.coordinate2
        return JsonResponse(ret)

    authentication_classes = [Authtication, ]

    def post(self, request):
        ret = {}
        collection_id = request.POST.get('collection_id')
        image = request.POST.get('image')
        label = request.POST.get('label')
        sub_label = request.POST.get('sub_label')
        coordinate1 = request.POST.get('coordinate1')
        coordinate2 = request.POST.get('coordinate2')
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
        photo = models.Photo_Info.objects.create(photo=image, label_id=label_object.id, collection_id=collection_id,
                                                 created_time=str(datetime.now()), sub_label=sub_label,
                                                 coordinate1=coordinate1, coordinate2=coordinate2)
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
        if not user:
            ret['code'] = 404
            ret['msg'] = 'token错误'
            return JsonResponse(ret)
        collection = models.Collection_Info.objects.filter(owner_id=user.id)
        collection_list = []
        for i in collection:
            image = models.Photo_Info.objects.filter(collection=i).first()
            dic = {
                'id': i.id,
                'name': i.name,
                'description': i.description,
                'created_time': i.created_time,
            }
            if not image:
                    dic['image'] = ''
            else:
                dic['image'] = image.photo
            collection_list.append(dic)
        ret['code'] = 200
        ret['username'] = user.email
        ret['collection_list'] = collection_list
        return JsonResponse(ret)


class Label(APIView):

    def get(self, request):
        ret = {}
        token = request.GET.get('token')
        collection_id = request.GET.get('collection_id')
        label_name = request.GET.get('label_name')
        if not models.User_Info.objects.filter(token=token):
            ret['code'] = 404
            return JsonResponse(ret)
        image = models.Photo_Info.objects.filter(label__label_name=label_name, collection_id=collection_id)
        photo_list = []
        for i in image:
            dic = {
                'image': i.photo,
                'sub_label': i.sub_label,
                'created_time': i.created_time,
                'coordinate1': i.coordinate1,
                'coordinate2': i.coordinate2,
            }
            photo_list.append(dic)
        ret['code'] = 200
        ret['photo_list'] = photo_list
        return JsonResponse(ret)


class Download(APIView):

    def get(self, request):
        collection_id = request.GET.get('collection_id')
        if not models.Collection_Info.objects.filter(id=collection_id):
            return HttpResponse(404)
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
        date = str(datetime.now())
        date = date.replace(' ', '-')
        date = date.replace(':', '-')
        with zipfile.ZipFile('./zip/images_%s.zip' % date, 'w', zipfile.ZIP_DEFLATED) as zip_fp:
            for i in images:
                image = i.photo.split(',')
                img_data = base64.b64decode(image[1])
                with zip_fp.open('image_%d.jpg' % i.id, 'w') as f:
                    f.write(img_data)
            with zip_fp.open('categories.json', 'w') as f:
                f.write(json.dumps(categories_data).encode("utf-8"))
        download_io.seek(0)
        return FileResponse(download_io, as_attachment=True, filename="images%s.zip" % date)


class Predict(APIView):

    # 此处传入的为base64编码
    def post(self, request):
        ret = {}
        # base64编码格式的图片
        image = request.POST.get('image')
        # 如果传入的为空图片，则返回报错信息，提示重新传图
        if image == '':
            ret['code'] = 404
            return JsonResponse(ret)
        # 处理为jpg格式图片,并以predict_img为名保存为jpg格式
        image = image.split(',')
        image = image[1]
        date = str(datetime.now())
        date = date.replace(' ', '-')
        date = date.replace(':', '-')
        img_path = r'./image/predict_img_%s.jpg' % date
        json_path = r'./json/class_indices.json'
        with open(img_path, 'wb') as f:
            img = base64.b64decode(image)
            f.write(img)

        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

        data_transform = transforms.Compose(
            [transforms.Resize(256),
             transforms.CenterCrop(224),
             transforms.ToTensor(),
             transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])])

        # 准备图像数据、类别信息数据
        assert os.path.exists(img_path), "file: '{}' dose not exist.".format(img_path)
        img = Image.open(img_path)
        img = data_transform(img)
        img = torch.unsqueeze(img, dim=0)
        assert os.path.exists(json_path), "file: '{}' dose not exist.".format(json_path)
        json_file = open(json_path, 'r')
        class_indict = json.load(json_file)

        # 创建模型
        model = MobileNetV2(num_classes=11).to(device)
        model_weight_path = './pth/MobileNetV2.pth'
        model.load_state_dict(torch.load(model_weight_path, map_location=device))
        model.eval()
        with torch.no_grad():
            # 预测类别信息
            output = torch.squeeze(model(img.to(device))).cpu()
            predict = torch.softmax(output, dim=0)
            predict_cla = torch.argmax(predict).numpy()
        # 类别结果信息
        img_classification = class_indict[str(predict_cla)]
        # 成功预测后返回成功状态码，类别信息
        # 不确定需不需要返回原始图片编码信息或者返回编码后的图片
        ret['code'] = 200
        ret['label'] = img_classification
        os.remove(img_path)
        return JsonResponse(ret)
