from django.shortcuts import render, redirect
from .. import models
from django import forms
from AdminSystem.utils.pagination import Pagination
from django.shortcuts import HttpResponse

def author_list(request):
    # 作者列表
    # 搜索涵盖的字段范围
    search_field = ["name__contains", "intro__contains", "author_id"]
    search_data = request.GET.get('q', "")

    orders = []
    if not orders:
        orders = ['author_id']
        
    data_dict = {}
    queryset = None
    if search_data:
        for search_key in search_field:
            if search_key == "author_id" and not search_data.isdigit() and search_data:
                data_dict = {}
                data_dict[search_key] = 0
            else:
                data_dict = {}
                data_dict[search_key] = search_data
            if not queryset:
                queryset = models.Author.objects.filter(**data_dict).order_by('author_id')
            else:
                queryset = queryset.union(models.Author.objects.filter(**data_dict).order_by('author_id'))
    else:
        queryset = models.Author.objects.filter(**data_dict).order_by(*orders)
    page_object = Pagination(request, queryset)

    context = {
        "search_data": search_data,

        "queryset": page_object.page_queryset,  # 分完页的数据
        "page_string": page_object.html()  # 页码
    }
    return render(request, 'author_list.html', context)



class AuthorModelForm(forms.ModelForm):
    class Meta:
        model = models.Author
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
            

class AuthorEditModelForm(forms.ModelForm):
    class Meta:
        model = models.Author
        # fields = "__all__"
        exclude = ['author_id']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 循环ModelForm中的所有字段，给每个字段的插件设置
        for name, field in self.fields.items():
            if name == 'intro':
                # field =forms.Textarea()
                field.widget.attrs = {
                "class": "form-control",
                "placeholder": 123
            }
            else:
                field.widget.attrs = {
                    "class": "form-control",
                    "placeholder": field.label
                }
            
def author_add(request):
    ''' 添加作者'''
    title = "新建作者"
    if request.method == "GET":
        form = AuthorModelForm()
        return render(request, 'change.html', {'form': form, "title": title})
    
    form = AuthorModelForm(data=request.POST)
    if form.is_valid():
        form.save()
        return redirect('/manager/author/list/')
    
    return render(request, 'change.html', {'form': form, "title": title})


def author_edit(request, nid):
    '''编辑作者'''
    title = "编辑作者"
    row_object = models.Author.objects.filter(author_id=nid).first()
    if not row_object:
        # 如果作者不存在
        # return render(request, 'error.html', {"msg": "数据不存在"})
        return redirect('/manager/author/list/')
    if request.method == "GET":
        form = AuthorEditModelForm(instance = row_object)
        return render(request, 'change.html', {"form": form, "title": title})
    
    form = AuthorEditModelForm(data=request.POST, instance=row_object)
    if form.is_valid():
        form.save()
        return redirect('/manager/author/list/')
    return render(request, 'change.html', {"form": form, "title": title})

def author_delete(request, nid):
    """ 删除作者 """
    try:
        models.Author.objects.filter(author_id=nid).delete()
    except:
        return HttpResponse('<h1>Error</h1><h3>无法删除</h3><br>可能是因为有该作（译）者 所编著的书籍<br>若一定要删除该栏目请先删除对应图书<br>先请返回')
    return redirect('/manager/author/list/')
