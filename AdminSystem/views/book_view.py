from django.shortcuts import render, redirect
from .. import models
from django import forms
from AdminSystem.utils.pagination import Pagination
import datetime
import random

def Unicode():
    val = random.randint(0x4e00, 0x9fbf)
    return chr(val)

def gen_random_book():
    author_tmp = models.Author.objects.all().first()
    for i in range(10000, 20000):
        title_num = random.randint(4,8)
        title_tmp = ""
        for j in range(title_num):
            title_tmp = title_tmp + Unicode()
        
        book=models.Book(book_id=i+100,title = title_tmp)
        book.save()

def book_list(request):
    # 书籍列表
    # 搜索涵盖的字段范围
    test_time = False
    if test_time:
        #插入随机数据
        # gen_random_book()
        search_field = ["title__contains"]
    else:
        search_field = ["book_id__contains", "title__contains", "press__name__contains", "introduction__contains","author__name__contains"]

    search_class_field = ["class_field__contains", "class_field_parent_class__contains"]
    # 可供用来排序的选项
    sort_field = [models.Book._meta.get_field('score'), 
                  models.Book._meta.get_field('price_standard'), 
                  models.Book._meta.get_field('press_id')]
    
    search_data = request.GET.get('q', "")
    search_class = request.GET.get('class_q', "")
    search_parent_class = request.GET.get('parent_class_q', "")
    
    sort_option = request.GET.get('orderby')
    sort_rule = request.GET.get('order')
    orders = []

    if test_time:
        # 测试时间
        starttime = datetime.datetime.now()
        for i in range(10000):
            if sort_option and sort_rule:
                if sort_rule == "asc":
                    orders.append(sort_option)
                if sort_rule == "desc":
                    orders.append('-' + sort_option)
            if not orders:
                orders = ['press_id']
            data_dict = {"class_field__name__contains":search_class, "class_field__parent_class__contains":search_parent_class}
            queryset = None
            if search_data:
                for search_key in search_field:
                    data_dict[search_key] = search_data
                    if not queryset:
                        queryset = models.Book.objects.filter(**data_dict).order_by('press_id')
                    else:
                        queryset = queryset.union(models.Book.objects.filter(**data_dict).order_by('press_id'))
                    del data_dict[search_key]
                if sort_option and sort_rule:
                    queryset = queryset.order_by(*orders)
            else:
                queryset = models.Book.objects.filter(**data_dict).order_by(*orders)
    
        endtime = datetime.datetime.now()
        print("搜索时间！！！")
        print( (endtime - starttime).seconds )
    else:
        if sort_option and sort_rule:
            if sort_rule == "asc":
                orders.append(sort_option)
            if sort_rule == "desc":
                orders.append('-' + sort_option)
        if not orders:
            orders = ['press_id']
        data_dict = {"class_field__name__contains":search_class, "class_field__parent_class__contains":search_parent_class}
        queryset = None
        if search_data:
            for search_key in search_field:
                data_dict[search_key] = search_data
                if not queryset:
                    queryset = models.Book.objects.filter(**data_dict).order_by('press_id')
                else:
                    queryset = queryset.union(models.Book.objects.filter(**data_dict).order_by('press_id'))
                del data_dict[search_key]
            if sort_option and sort_rule:
                queryset = queryset.order_by(*orders)
        else:
            queryset = models.Book.objects.filter(**data_dict).order_by(*orders)

    page_object = Pagination(request, queryset)

    # 此处是缩减简介长度
    extract = {}
    for book in queryset:
        if book.introduction:
            extract[book.book_id] = book.introduction[0:140] + '...'
        else:
            extract[book.book_id] = '暂无简介'


    if sort_option:
        sort_option = models.Book._meta.get_field(sort_option)
    context = {
        "search_data": search_data,
        "sort_field": sort_field,
        "sort_option": sort_option,
        "sort_rule": sort_rule,
        "extract":extract,

        "search_class":search_class,
        "search_parent_class":search_parent_class,

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

    models.BookAuthor.objects.filter(book_id=nid).delete()
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