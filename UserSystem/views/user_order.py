import copy
from pyexpat import model
from tokenize import Number
from django import forms
from django.utils import timezone
from django.shortcuts import render, redirect, HttpResponse
from AdminSystem.utils.pagination import Pagination
from AdminSystem import models

def get_context_for_unsub_order(info_dict, warning=None):
    nid = info_dict["id"]
    filter_dict = {}
    filter_dict["user_id"] = nid
    filter_dict["submission_time"] = None
    unsubmitted_order = models.Order.objects.filter(**filter_dict).first()
    # 如果该用户没有未提交的订单，就创建一个
    if unsubmitted_order is None:
        current_user = models.User.objects.filter(user_id=nid).first()
        unsubmitted_order = models.Order(user_id = nid, submission_time = None, telephone = current_user.telephone, address=current_user.address, name=current_user.name)
        unsubmitted_order.save()
    unsubmitted_order_list = models.OrderList.objects.filter(order_id=unsubmitted_order.order_id)
    context = {
        "order": unsubmitted_order,
        "order_list": unsubmitted_order_list,
        "warning_info":None,
    }
    return context

def show_unsubmitted_order(request):
    '''显示用户未提交的order信息,如果没有,就新建一个'''
    title = "显示用户未提交订单信息"
    info_dict = request.session.get("info")
    context = get_context_for_unsub_order(info_dict)
    return render(request, 'unsub_order.html', context)


def submit_unsubmitted_order(request):
    '''提交订单,把订单状态改为已提交,检验各字段不能为空'''
    info_dict = request.session.get("info")
    context = get_context_for_unsub_order(info_dict)
    unsubmitted_order = context["order"]
    unsubmitted_order_list = context["order_list"]
    if  (unsubmitted_order.telephone is not None) and (unsubmitted_order.address is not None) and (unsubmitted_order.name is not None):
        if  len(unsubmitted_order_list) != 0 :
            unsubmitted_order.submission_time = timezone.now()
            unsubmitted_order.status = "已付款"
            unsubmitted_order.save()
            return redirect('/dsdouban/order/submitted_orders/')
        else:
            context["warning_info"] = "购物车还没有东西！"
            return render(request, 'unsub_order.html', context)
    else:
        context["warning_info"] = "订单信息不完整，请确保收件人信息完整！"
        return render(request, 'unsub_order.html', context)

class OrderModelForm(forms.ModelForm):
    class Meta:
        model = models.Order
        # fields = "__all__"
        fields = ['logistics', 'telephone', 'address', 'name']
        
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
    
    ''' 修改订单'''
    title = "修改订单信息"
    if request.method == "GET":
        form = OrderModelForm()
        return render(request, 'unsub_order_change.html', {'form': form, "title": title})
    
    form = OrderModelForm(data=request.POST, instance=row_object)
    if form.is_valid():
        form.save()
        return redirect('/dsdouban/order/unsubmitted_order/')
    
    return render(request, 'unsub_order_change.html', {'form': form, "title": title})

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
    book_object = models.Book.objects.filter(book_id=row_object.book_id).first()
    
    ''' 修改订单列表书籍数目'''
    title = "修改订单列表书籍数目"
    if request.method == "GET":
        form = OrderListModelForm()
        return render(request, 'unsub_order_list_change.html', {'form': form, "title": title, "order":row_object,"book":book_object})
    
    form = OrderListModelForm(data=request.POST, instance=row_object)
    if form.is_valid():
        form.save()
        return redirect('/dsdouban/order/unsubmitted_order/')
    
    return render(request, 'unsub_order_list_change.html', {'form': form, "title": title, "order":row_object,"book":book_object})

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
        unsubmitted_order = models.Order(user_id = user_nid, submission_time = None)
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
    search_field = ['order_id', 'user__name__contains', 'name__contains']    # Search by order_id or username
    # 获取用户id
    info_dict = request.session.get("info")
    user_nid = info_dict["id"]
    search_data = request.GET.get('q', "")

    # 按order id 降序排列
    orders = []
    if not orders:
        orders = ['-order_id']

    data_dict = {"user_id":user_nid}
    queryset = None
    if search_data:
        for search_key in search_field:
            if search_key == 'order_id':
                data_dict = {"user_id":user_nid}
                if search_data.isnumeric(): # In order_id search, we should make sure that input is number
                    data_dict[search_key] = eval(search_data)
                else:
                    continue
            else:
                data_dict = {"user_id":user_nid}
                data_dict[search_key] = search_data
            if not queryset:
                queryset = models.Order.objects.filter(**data_dict).exclude(submission_time = None).order_by(*orders)
            else:
                queryset = queryset.union(models.Order.objects.filter(**data_dict).exclude(submission_time=None).order_by(*orders))
    else:
        queryset = models.Order.objects.filter(**data_dict).exclude(submission_time=None).order_by(*orders)

    queryset_dict = {}

    for order_item in queryset:
        queryset_dict[order_item.order_id] = models.OrderList.objects.filter(order_id=order_item.order_id)

    page_object = Pagination(request, queryset)

    

    context = {
        "search_data": search_data,
        "queryset": page_object.page_queryset,  # 分完页的数据
        "page_string": page_object.html(),  # 页码
        "detail": queryset_dict
    }
    return render(request, 'user_order_list.html', context)


def show_submitted_order_details(request, nid):
    '''展示已提交的订单细节,nid为order_id,几乎与show_unsubmitted_order一样'''
    order = models.Order.objects.filter(order_id=nid).first()
    order_list = models.OrderList.objects.filter(order_id=order.order_id)
    context = {
        "order": order,
        "order_list": order_list,
        "warning_info": None,
    }
    return render(request, 'sub_order_details.html', context)

def cancel_submitted_order(request, nid):
    '''取消已提交的订单,改status为已取消,返回一个,即将退款的页面,可以直接用httpresponse'''
    '''nid为order_id'''
    row_object = models.Order.objects.filter(order_id=nid).first()
    row_object.status = "已取消"
    row_object.save()
    return redirect('/dsdouban/order/submitted_orders/')

def finish_submitted_order(request, nid):
    '''确认收货,完成订单,改status为已完成'''
    '''nid为order_id'''
    row_object = models.Order.objects.filter(order_id=nid).first()
    row_object.status = "已完成"
    row_object.save()
    return redirect('/dsdouban/order/submitted_orders/')

def edit_submitted_order(request, nid):
    '''编辑已提交的订单,但不能编辑已完成和取消的订单,只可以编辑收货人,电话和收货地址'''
    '''nid为order_id'''
    # nid 是订单号
    row_object = models.Order.objects.filter(order_id=nid).first()
    
    ''' 修改订单'''
    title = "修改订单信息"
    if request.method == "GET":
        form = OrderModelForm()
        return render(request, 'sub_order_change.html', {'form': form, "title": title})
    
    form = OrderModelForm(data=request.POST, instance=row_object)
    if form.is_valid():
        form.save()
        return redirect('/dsdouban/order/' + str(row_object.order_id) + '/detail_order/')
    
    return render(request, 'sub_order_change.html', {'form': form, "title": title})