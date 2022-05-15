import copy
from django import forms
from django.utils import timezone
from django.shortcuts import render, redirect
from AdminSystem.utils.pagination import Pagination

from AdminSystem import models

def book_list(request):
    # 书籍列表
    search_data = request.GET.get('q', "")
    sort_option = request.GET.get('orderby')
    sort_rule = request.GET.get('order')

    search_field = ["book_id__contains", "title__contains", "press__name__contains", "introduction__contains"]
    sort_field = [models.Book._meta.get_field('score'), 
                  models.Book._meta.get_field('price_standard'), 
                  models.Book._meta.get_field('press_id')]

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
    return render(request, 'user_book_list.html', context)



class CommentModelForm(forms.ModelForm):
    class Meta:
        model = models.Comments
        # fields = "__all__"
        fields = ['comment']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 循环ModelForm中的所有字段，给每个字段的插件设置
        for name, field in self.fields.items():
            field.widget.attrs = {
                "class": "form-control",
                "placeholder": field.label
            }



def book_details(request, nid):
    '''显示书籍细节信息'''
    row_object = models.Book.objects.filter(book_id=nid).first()
    obj_comments = models.Comments.objects.filter(book_id=nid)
    info_dict = request.session.get("info")
    title = "新建评论"
    if request.method == "GET":
        form = CommentModelForm()
        return render(request, 'user_book_details.html', {'form': form, "title": title, "obj":row_object,"comments":obj_comments})
    ''' 添加评论'''
    comment_data = request.POST.copy()
    book_obj = models.Book.objects.filter(book_id=nid).first()
    user_obj = models.User.objects.filter(user_id=info_dict['id']).first()
    if user_obj is None:
        user_obj = models.Admin.objects.filter(id=info_dict['id']).first()

    form = CommentModelForm(data=comment_data)
    if form.is_valid():
        form.instance.book = book_obj
        form.instance.user = user_obj
        form.instance.submission_time = timezone.now()
        form.save()
        return redirect('/dsdouban/book/'+str(nid)+'/details/')
    return render(request, 'user_book_details.html', {'form': form, "title": title, "obj":row_object})


    
