from django.db import models


# Create your models here.

class User_Info(models.Model):  # 用户信息
    email = models.TextField(default='')
    password = models.TextField(max_length=32, default='')
    user_type = models.IntegerField(default=1)
    token = models.TextField(default='')


class Collection_Info(models.Model):  # 数据集信息
    name = models.TextField(max_length=1024, default='Untitled')
    collection_type = models.IntegerField(default=0)
    permission = models.IntegerField(default=0)
    description = models.TextField(max_length=2048, default='')
    created_time = models.TextField(default='')
    owner = models.ForeignKey('User_Info', on_delete=models.CASCADE)
    photo_number = models.IntegerField(default='0')
    class_number = models.IntegerField(default='0')
    order = models.ForeignKey('Order_Info', on_delete=models.CASCADE, null=True, blank=True, default=None)


class Label_Info(models.Model):  # 类别信息
    label_name = models.TextField(max_length=32, default='')
    number = models.IntegerField(default=0)
    belonging = models.ForeignKey('Collection_Info', on_delete=models.CASCADE)


class Photo_Info(models.Model):  # 图片信息
    photo = models.TextField()
    label = models.ForeignKey('Label_Info', on_delete=models.CASCADE)
    created_time = models.TextField(default='')
    sub_label = models.TextField(default='')
    collection = models.ForeignKey('Collection_Info', on_delete=models.CASCADE)
    coordinate1 = models.TextField()
    coordinate2 = models.TextField()


class Message(models.Model):  # 修正信息
    sender = models.ForeignKey('User_Info', on_delete=models.CASCADE)
    receiver = models.ForeignKey('User_Info', on_delete=models.CASCADE)
    photo_id = models.TextField(default='')
    image = models.TextField(default='')
    label = models.TextField(default='')
    sub_label = models.TextField(default='')
    coordinate1 = models.TextField(default='')
    coordinate2 = models.TextField(default='')


class Order_Info(models.Model):  # 数据订单需求
    order_name = models.TextField(default='')
    owner = models.ForeignKey('User_Info', on_delete=models.CASCADE)
    order_type = models.IntegerField(default=0)
    amount_of_data = models.IntegerField(default=0)
    description = models.TextField(default='')
    started_time = models.TextField(default='')
    created_time = models.TextField(default='')
    collection = models.ForeignKey('Collection_Info', on_delete=models.CASCADE)
