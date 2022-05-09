from django.shortcuts import render, redirect
from .. import models
from django import forms
from AdminSystem.utils.pagination import Pagination


def order_list(request):
    search_field = ['order_id', 'user__name__contains', 'name__contains']    # Search by order_id or username
    
    sort_field = []

    search_data = request.GET.get('q', "")
    # sort_option = request.GET.get('orderby')
    # sort_rule = request.GET.get('order')
    orders = []

    if not orders:
        orders = ['order_id']

    data_dict = {}
    queryset = None
    if search_data:
        for search_key in search_field:
            if search_key == 'order_id':
                data_dict = {}
                if search_data.isnumeric(): # In order_id search, we should make sure that input is number
                    data_dict[search_key] = eval(search_data)
                else:
                    continue
            else:
                data_dict = {}
                data_dict[search_key] = search_data
            if not queryset:
                queryset = models.Order.objects.filter(**data_dict).exclude(submission_time = None).order_by(*orders)
            else:
                queryset = queryset.union(models.Order.objects.filter(**data_dict).exclude(submission_time=None).order_by(*orders))
    else:
        queryset = models.Order.objects.filter(**data_dict).exclude(submission_time=None).order_by(*orders)
    page_object = Pagination(request, queryset)

    context = {
        "search_data": search_data,
        # "sort_field": sort_field,
        # "sort_option": sort_option,
        # "sort_rule": sort_rule,

        "queryset": page_object.page_queryset,  # 分完页的数据
        "page_string": page_object.html()  # 页码
    }
    return render(request, 'order_list.html', context)

def order_details(request, nid):
    order = models.Order.objects.filter(order_id=nid).first()
    order_list = models.OrderList.objects.filter(order_id=nid)
    sum = 0.0
    for i in range(len(order_list)):
        num = order_list[i].number
        price = models.Book.objects.filter(book_id=order_list[i].book_id).first().price_standard
        sum = sum + num * float(price)
    context = {
        "order": order,
        "order_list": order_list,
        "sum": sum
    }
    return render(request, 'order_details.html', context)

def order_delete(request, nid):
    models.OrderList.objects.filter(order_id=nid).delete()
    models.Order.objects.filter(order_id=nid).delete()
    return redirect('/manager/order/list/')

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

def edit_order(request, nid):
    # nid 是订单号
    row_object = models.Order.objects.filter(order_id=nid).first()
    
    ''' 修改订单'''
    title = "修改订单信息"
    if request.method == "GET":
        form = OrderModelForm()
        return render(request, 'change.html', {'form': form, "title": title})
    
    form = OrderModelForm(data=request.POST, instance=row_object)
    if form.is_valid():
        form.save()
        return redirect('/manager/order/' + str(row_object.order_id) + '/details/')


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
            
def edit_order_list(request, nid):
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
        if row_object.number:
            return redirect('/manager/order/' + str(row_object.order_id) + '/details/')
        else:
            return redirect('/manager/orderlist/' + str(row_object.order_list_id) + '/delete/')
    
    return render(request, 'change.html', {'form': form, "title": title})

def order_list_delete(request, nid):
    # orderid = models.OrderList.objects.filter(order_list_id=nid)#.values('order_id')
    orderid = models.OrderList.objects.filter(order_list_id=nid).values('order_id')[0]['order_id']
    models.OrderList.objects.filter(order_list_id=nid).delete()
    return redirect('/manager/order/' + str(orderid) + '/details/')