from django.db import models


# Create your models here.

class User_Info(models.Model):  # 用户信息
    email = models.TextField(default='')
    password = models.TextField(max_length=32, default='')
    token = models.TextField(default='')


class Collection_Info(models.Model):  # 数据集信息
    name = models.TextField(max_length=1024, default='Untitled')
    owner = models.ForeignKey('User_Info', on_delete=models.CASCADE)
    photo_number = models.IntegerField(default='0')
    class_number = models.IntegerField(default='0')


class Label_Info(models.Model):  # 类别信息
    label_name = models.TextField(max_length=32, default='')
    number = models.IntegerField(default=0)
    belonging = models.ForeignKey('Collection_Info', on_delete=models.CASCADE)


class Photo_Info(models.Model):  # 图片信息
    photo = models.TextField()
    label = models.ForeignKey('Label_Info', on_delete=models.CASCADE)
    collection = models.ForeignKey('Collection_Info', on_delete=models.CASCADE)
