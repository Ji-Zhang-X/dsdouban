import copy
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
    if unsubmitted_order is None:
        unsubmitted_order = models.Order(user_id = nid, submission_time = None)
        unsubmitted_order.save()
    unsubmitted_order_list = models.OrderList.objects.filter(order_id=unsubmitted_order.order_id)
    print(unsubmitted_order_list)
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
    
    #request.session["info"] = {'id': user_object.user_id, 'name': user_object.name, 'auth': "user"}
    info_dict = request.session.get("info")
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
    #request.session["info"] = {'id': user_object.user_id, 'name': user_object.name, 'auth': "user"}

    info_dict = request.session.get("info")
    ''' 修改订单列表,未完成'''
    title = "修改订单列表"
    if request.method == "GET":
        form = OrderListModelForm()
        return render(request, 'change.html', {'form': form, "title": title})
    
    comment_data = request.POST.copy()
    book_obj = models.Book.objects.filter(book_id=nid).first()
    user_obj = models.User.objects.filter(user_id=info_dict['id']).first()
    if user_obj is None:
        user_obj = models.Admin.objects.filter(id=info_dict['id']).first()

    form = OrderListModelForm(data=comment_data)
    if form.is_valid():
        form.instance.book = book_obj
        form.instance.user = user_obj
        form.instance.submission_time = timezone.now()
        form.save()
        return redirect('/dsdouban/book/'+str(nid)+'/details/')
    
    return render(request, 'change.html', {'form': form, "title": title})

def add_book_to_unsubmitted_order_list(request, nid):
    '''在图书详情页面点击添加到我的订单之后,
       将book_id=nid的书籍添加到该用户未提交订单的订单列表中,
       并且跳转到查看订单页面
    '''
    pass

def show_submitted_orders(request):
    '''查看用户已提交的订单'''
    pass