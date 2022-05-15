from django.shortcuts import render, redirect
from .. import models
from django import forms
from AdminSystem.utils.pagination import Pagination

def book_list(request):
    # 书籍列表
    # 搜索涵盖的字段范围
    search_field = ["press__name__contains", "introduction__contains"]
    # 可供用来排序的选项
    sort_field = [models.Book._meta.get_field('score'), 
                  models.Book._meta.get_field('price_standard'), 
                  models.Book._meta.get_field('press_id')]
    
    search_data = request.GET.get('q', "")
    sort_option = request.GET.get('orderby')
    sort_rule = request.GET.get('order')
    orders = []
    if sort_option and sort_rule:
        if sort_rule == "asc":
            orders.append(sort_option)
        if sort_rule == "desc":
            orders.append('-' + sort_option)
    if not orders:
        orders = ['book_id']
        
    data_dict = {}
    queryset = None
    if search_data:
        for search_key in search_field:
            data_dict = {}
            data_dict[search_key] = search_data
            if not queryset:
                queryset = models.Book.objects.filter(**data_dict).order_by(*orders)
            else:
                queryset = queryset.union(models.Book.objects.filter(**data_dict).order_by(*orders))
        queryset = queryset.order_by(*orders)
    else:
        queryset = models.Book.objects.filter(**data_dict).order_by(*orders)
    page_object = Pagination(request, queryset)

    if sort_option:
        sort_option = models.Book._meta.get_field(sort_option)
    context = {
        "search_data": search_data,
        "sort_field": sort_field,
        "sort_option": sort_option,
        "sort_rule": sort_rule,

        "queryset": page_object.page_queryset,  # 分完页的数据
        "page_string": page_object.html()  # 页码
    }
    return render(request, 'book_list.html', context)



class bookModelForm(forms.ModelForm):
    class Meta:
        model = models.Book
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
            
    def clean_book_id(self):
        txt_book_id = self.cleaned_data["book_id"]

        exists = models.Book.objects.filter(book_id=txt_book_id).exists()
        if exists:
            raise ValidationError("书籍已存在")

        # 验证通过，用户输入的值返回
        return txt_book_id

class bookEditModelForm(forms.ModelForm):
    class Meta:
        model = models.Book
        # fields = "__all__"
        exclude = ['book_id']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 循环ModelForm中的所有字段，给每个字段的插件设置
        for name, field in self.fields.items():
            field.widget.attrs = {
                "class": "form-control",
                "placeholder": field.label
            }
            
            
def book_add(request):
    ''' 添加书籍'''
    title = "新建书籍"
    if request.method == "GET":
        form = bookModelForm()
        return render(request, 'change.html', {'form': form, "title": title})
    
    form = bookModelForm(data=request.POST)
    if form.is_valid():
        form.save()
        return redirect('/manager/book/list/')
    
    return render(request, 'change.html', {'form': form, "title": title})


def book_edit(request, nid):
    '''编辑书籍'''
    title = "编辑书籍"
    row_object = models.Book.objects.filter(book_id=nid).first()
    if not row_object:
        # 如果书籍不存在
        # return render(request, 'error.html', {"msg": "数据不存在"})
        return redirect('/manager/book/list/')
    if request.method == "GET":
        form = bookEditModelForm(instance = row_object)
        return render(request, 'change.html', {"form": form, "title": title})
    
    form = bookEditModelForm(data=request.POST, instance=row_object)
    if form.is_valid():
        form.save()
        return redirect('/manager/book/list/')
    return render(request, 'change.html', {"form": form, "title": title})

def book_delete(request, nid):
    """ 删除书籍 """
    models.Book.objects.filter(book_id=nid).delete()
    return redirect('/manager/book/list/')

def book_details(request, nid):
    '''显示书籍细节信息'''
    title = "显示书籍细节信息"
    row_object = models.Book.objects.filter(book_id=nid).first()
    obj_comments = models.Comments.objects.filter(book_id=nid)
    return render(request, 'book_details.html', {"obj": row_object,"comments":obj_comments})

def comment_delete(request, nid, book_id):
    # nid is comment_id
    models.Comments.objects.filter(comment_id=nid).update(comment="由于违反社区规范，该评论已被删除！")
    # return redirect('/manager/book/list/')
    return redirect('/manager/book/'+str(book_id)+'/details/')