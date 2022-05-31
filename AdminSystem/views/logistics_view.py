from django.shortcuts import render, redirect
from .. import models
from django import forms
from AdminSystem.utils.pagination import Pagination
from django.shortcuts import HttpResponse

def logistics_list(request):
    # 物流列表
    # 搜索涵盖的字段范围
    search_field = ["logistics_name__contains", "logistics_id", "logistics_tele"]
    search_data = request.GET.get('q', "")

    orders = []
    if not orders:
        orders = ['logistics_id']
        
    data_dict = {}
    queryset = None
    if search_data:
        for search_key in search_field:
            data_dict = {}
            data_dict[search_key] = search_data
            if not queryset:
                queryset = models.Logistics.objects.filter(**data_dict).order_by(*orders)
            else:
                queryset = queryset.union(models.Logistics.objects.filter(**data_dict).order_by(*orders))
    else:
        queryset = models.Logistics.objects.filter(**data_dict).order_by(*orders)
    page_object = Pagination(request, queryset)

    context = {
        "search_data": search_data,

        "queryset": page_object.page_queryset,  # 分完页的数据
        "page_string": page_object.html()  # 页码
    }
    return render(request, 'logistics_list.html', context)



class logisticsModelForm(forms.ModelForm):
    class Meta:
        model = models.Logistics
        fields = "__all__"
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 循环ModelForm中的所有字段，给每个字段的插件设置
        for name, field in self.fields.items():
            field.widget.attrs = {
                "class": "form-control",
                "placeholder": field.label
            }
            

class logisticsEditModelForm(forms.ModelForm):
    class Meta:
        model = models.Logistics
        # fields = "__all__"
        exclude = ['logistics_id']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 循环ModelForm中的所有字段，给每个字段的插件设置
        for name, field in self.fields.items():
            field.widget.attrs = {
                "class": "form-control",
                "placeholder": field.label
            }
            
            
def logistics_add(request):
    ''' 添加物流'''
    title = "新建物流"
    if request.method == "GET":
        form = logisticsModelForm()
        return render(request, 'change.html', {'form': form, "title": title})
    
    form = logisticsModelForm(data=request.POST)
    if form.is_valid():
        form.save()
        return redirect('/manager/logistics/list/')
    
    return render(request, 'change.html', {'form': form, "title": title})


def logistics_edit(request, nid):
    '''编辑物流'''
    title = "编辑物流"
    row_object = models.Logistics.objects.filter(logistics_id=nid).first()
    if not row_object:
        # 如果物流不存在
        return redirect('/manager/logistics/list/')
    if request.method == "GET":
        form = logisticsEditModelForm(instance = row_object)
        return render(request, 'change.html', {"form": form, "title": title})
    
    form = logisticsEditModelForm(data=request.POST, instance=row_object)
    if form.is_valid():
        form.save()
        return redirect('/manager/logistics/list/')
    return render(request, 'change.html', {"form": form, "title": title})

def logistics_delete(request, nid):
    """ 删除物流 """
    try:
        models.Logistics.objects.filter(logistics_id=nid).delete()
    except:
        return HttpResponse('<h1>Error</h1><h3>无法删除</h3><br>可能是因为有该物流公司仍有物流记录<br>若一定要删除该栏目请先删除对应记录<br>先请返回')

    return redirect('/manager/logistics/list/')
