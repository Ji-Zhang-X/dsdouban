from django.shortcuts import render, redirect
from .. import models
from django import forms
from AdminSystem.utils.pagination import Pagination


def order_list(request):
    search_field = ['order_id', 'user__name__contains']    # Search by order_id or username
    
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
                data_dict = {}
                data_dict[search_key] = search_data
            if not queryset:
                queryset = models.Order.objects.filter(**data_dict).order_by(*orders)
            else:
                queryset.union(models.Order.objects.filter(**data_dict).order_by(*orders))
    else:
        queryset = models.Order.objects.filter(**data_dict).order_by(*orders)
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
    context = {
        "order": order,
        "order_list": order_list
    }
    return render(request, 'order_details.html', context)

def order_delete(request, nid):
    models.Order.objects.filter(order_id=nid).delete()
    return redirect('/manager/order/list/')