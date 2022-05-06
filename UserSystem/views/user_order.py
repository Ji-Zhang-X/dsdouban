import copy
from tokenize import Number
from django import forms
from django.utils import timezone
from django.shortcuts import render, redirect, HttpResponse
from AdminSystem.utils.pagination import Pagination

from AdminSystem import models

def show_unsubmitted_order(request):
    '''显示用户未提交的order信息,如果没有,就新建一个'''
    title = "显示用户未提交订单信息"
    info_dict = request.session.get("info")
    nid = info_dict["id"]
    filter_dict = {}
    filter_dict["user_id"] = nid
    filter_dict["submission_time"] = None
    unsubmitted_order = models.Order.objects.filter(**filter_dict).first()
    # 如果该用户没有未提交的订单，就创建一个
    if unsubmitted_order is None:
        unsubmitted_order = models.Order(user_id = nid, submission_time = None)
        unsubmitted_order.save()
    unsubmitted_order_list = models.OrderList.objects.filter(order_id=unsubmitted_order.order_id)
    return render(request, 'unsub_order.html', {"order": unsubmitted_order,"order_list":unsubmitted_order_list})

            
class OrderModelForm(forms.ModelForm):
    class Meta:
        model = models.Order
        # fields = "__all__"
        fields = ['logistics']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 循环ModelForm中的所有字段，给每个字段的插件设置
        for name, field in self.fields.items():
            field.widget.attrs = {
                "class": "form-control",
                "placeholder": field.label
            }

def edit_unsubmitted_order(request, nid):
    # nid 是订单号
    row_object = models.Order.objects.filter(order_id=nid).first()
    
    ''' 修改物流'''
    title = "修改订单物流"
    if request.method == "GET":
        form = OrderModelForm()
        return render(request, 'change.html', {'form': form, "title": title})
    
    form = OrderModelForm(data=request.POST, instance=row_object)
    if form.is_valid():
        form.save()
        return redirect('/dsdouban/order/unsubmitted_order/')
    
    return render(request, 'change.html', {'form': form, "title": title})

class OrderListModelForm(forms.ModelForm):
    class Meta:
        model = models.OrderList
        # fields = "__all__"
        fields = ['number']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 循环ModelForm中的所有字段，给每个字段的插件设置
        for name, field in self.fields.items():
            field.widget.attrs = {
                "class": "form-control",
                "placeholder": field.label
            }
            
def edit_unsubmitted_order_list(request, nid):
    # nid 是order_list号
    row_object = models.OrderList.objects.filter(order_list_id=nid).first()
    
    ''' 修改订单列表书籍数目'''
    title = "修改订单列表书籍数目"
    if request.method == "GET":
        form = OrderListModelForm()
        return render(request, 'change.html', {'form': form, "title": title})
    
    form = OrderListModelForm(data=request.POST, instance=row_object)
    if form.is_valid():
        form.save()
        return redirect('/dsdouban/order/unsubmitted_order/')
    
    return render(request, 'change.html', {'form': form, "title": title})

def delete_unsubmitted_order_list(request, nid):
    # 删除订单列表中的某本书籍
    row_object = models.OrderList.objects.filter(order_list_id=nid).delete()
    return redirect('/dsdouban/order/unsubmitted_order/')

def add_book_to_unsubmitted_order_list(request, nid):
    '''在图书详情页面点击添加到我的订单之后,
       将book_id=nid的书籍添加到该用户未提交订单的订单列表中,
       并且跳转到查看订单页面
    '''
    title = "显示用户未提交订单信息"
    info_dict = request.session.get("info")
    user_nid = info_dict["id"]
    filter_dict = {}
    filter_dict["user_id"] = user_nid
    filter_dict["submission_time"] = None
    unsubmitted_order = models.Order.objects.filter(**filter_dict).first()
    # 如果该用户没有未提交的订单，就创建一个
    if unsubmitted_order is None:
        unsubmitted_order = models.Order(user_id = nid, submission_time = None)
        unsubmitted_order.save()
    # 查询该书籍是否在订单列表中
    book_order_list_item = models.OrderList.objects.filter(order_id=unsubmitted_order.order_id, book_id = nid).first()
    # 如果该书籍不在订单列表中，就加进去
    if book_order_list_item is None:
        book_order_list_item = models.OrderList(order_id=unsubmitted_order.order_id, book_id = nid, number=1)
        book_order_list_item.save()
    # 先获得已有的所有order_list
    unsubmitted_order_list = models.OrderList.objects.filter(order_id=unsubmitted_order.order_id)

    return render(request, 'unsub_order.html', {"order": unsubmitted_order,"order_list":unsubmitted_order_list})

def show_submitted_orders(request):
    '''查看用户已提交的订单'''
    pass