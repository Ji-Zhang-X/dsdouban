from django.shortcuts import render, redirect
from .. import models
from django import forms
from AdminSystem.utils.pagination import Pagination

def press_list(request):
    # 出版社列表
    # 搜索涵盖的字段范围
    search_field = ["name__contains", "address__contains"]
    search_data = request.GET.get('q', "")

    orders = []
    if not orders:
        orders = ['press_id']
        
    data_dict = {}
    queryset = None
    if search_data:
        for search_key in search_field:
            data_dict = {}
            data_dict[search_key] = search_data
            if not queryset:
                queryset = models.Press.objects.filter(**data_dict).order_by(*orders)
            else:
                queryset = queryset.union(models.Press.objects.filter(**data_dict).order_by(*orders))
    else:
        queryset = models.Press.objects.filter(**data_dict).order_by(*orders)
    page_object = Pagination(request, queryset)

    context = {
        "search_data": search_data,

        "queryset": page_object.page_queryset,  # 分完页的数据
        "page_string": page_object.html()  # 页码
    }
    return render(request, 'press_list.html', context)



class PressModelForm(forms.ModelForm):
    class Meta:
        model = models.Press
        fields = "__all__"
        # exclude = ['book_id']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 循环ModelForm中的所有字段，给每个字段的插件设置
        for name, field in self.fields.items():
            field.widget.attrs = {
                "class": "form-control",
                "placeholder": field.label
            }
            

class PressEditModelForm(forms.ModelForm):
    class Meta:
        model = models.Press
        # fields = "__all__"
        exclude = ['press_id']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 循环ModelForm中的所有字段，给每个字段的插件设置
        for name, field in self.fields.items():
            field.widget.attrs = {
                "class": "form-control",
                "placeholder": field.label
            }
            
            
def press_add(request):
    ''' 添加出版社'''
    title = "新建出版社"
    if request.method == "GET":
        form = PressModelForm()
        return render(request, 'change.html', {'form': form, "title": title})
    
    form = PressModelForm(data=request.POST)
    if form.is_valid():
        form.save()
        return redirect('/manager/press/list/')
    
    return render(request, 'change.html', {'form': form, "title": title})


def press_edit(request, nid):
    '''编辑出版社'''
    title = "编辑出版社"
    row_object = models.Press.objects.filter(press_id=nid).first()
    if not row_object:
        # 如果出版社不存在
        return redirect('/manager/press/list/')
    if request.method == "GET":
        form = PressEditModelForm(instance = row_object)
        return render(request, 'change.html', {"form": form, "title": title})
    
    form = PressEditModelForm(data=request.POST, instance=row_object)
    if form.is_valid():
        form.save()
        return redirect('/manager/press/list/')
    return render(request, 'change.html', {"form": form, "title": title})

def press_delete(request, nid):
    """ 删除出版社 """
    models.Press.objects.filter(press_id=nid).delete()
    return redirect('/manager/press/list/')
