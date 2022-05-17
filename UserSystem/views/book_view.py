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
        orders = ['press_id']
   
    data_dict = {}
    queryset = None
    if search_data:
        for search_key in search_field:
            data_dict = {}
            data_dict[search_key] = search_data
            if not queryset:
                queryset = models.Book.objects.filter(**data_dict).order_by("press_id")
            else:
                queryset = queryset.union(models.Book.objects.filter(**data_dict).order_by("press_id"))
        if sort_option and sort_rule:
            queryset = queryset.order_by(*orders)
    else:
        queryset = models.Book.objects.filter(**data_dict).order_by("press_id")
    page_object = Pagination(request, queryset)

    # 此处是缩减简介长度
    extract = {}
    for book in queryset:
        extract[book.book_id] = book.introduction[0:140] + '...'

    if sort_option:
        sort_option = models.Book._meta.get_field(sort_option)
    context = {
        "search_data": search_data,
        "sort_field": sort_field,
        "sort_option": sort_option,
        "sort_rule": sort_rule,
        "extract":extract,
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

class RankModelForm(forms.ModelForm):
    class Meta:
        model = models.Mark
        # fields = "__all__"
        fields = ['marks']
        
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
    info_dict = request.session.get("info")
    book_obj = models.Book.objects.filter(book_id=nid).first()
    user_obj = models.User.objects.filter(user_id=info_dict['id']).first()
    if user_obj is None:
        user_obj = models.Admin.objects.filter(id=info_dict['id']).first()
    obj_comments = models.Comments.objects.filter(book_id=nid)
    title = "新建评论"

    # 查看有没有已经评了分数的
    rank_obj = models.Mark.objects.filter(user_id=user_obj.user_id,book_id=nid).first()
    if rank_obj is not None:
        rank_score = int(rank_obj.marks)
    else:
        rank_score = 0
    
    if request.method == "GET":
        form = CommentModelForm()
        context = {'form': form, "title": title, "obj":book_obj,
                    "comments":obj_comments, "user":user_obj, 'rank_score':rank_score}
        return render(request, 'user_book_details.html', context)
    

    ''' 添加评论 与评分系统'''
    post_data = request.POST.copy()
    if post_data.get('marks') == None: # 进入评论系统
        comment_data = post_data
        form = CommentModelForm(data=comment_data)
        if form.is_valid():
            form.instance.book = book_obj
            form.instance.user = user_obj
            form.instance.submission_time = timezone.now()
            form.save()
            return redirect('/dsdouban/book/'+str(nid)+'/details/')
        return render(request, 'user_book_details.html', {'form': form, "title": title, "obj":book_obj, "comments":obj_comments, "user":user_obj})
    # 进入评分系统
    if rank_obj is None:
        form = RankModelForm(data=post_data)
    else:
        form = RankModelForm(instance=rank_obj, data=post_data)

    if form.is_valid():
        form.instance.book = book_obj
        form.instance.user = user_obj
        form.instance.ranks = str(post_data['marks'])
        form.save()
        return redirect('/dsdouban/book/'+str(nid)+'/details/')
    return render(request, 'user_book_details.html', {"title": title, "obj":book_obj, "comments":obj_comments, "user":user_obj})
    
    

def comment_delete(request, nid):
    row_obj = models.Comments.objects.filter(comment_id=nid).first()
    book_id = row_obj.book_id
    row_obj.delete()
    # models.Comments.objects.filter(comment_id=nid).delete()
    return redirect('/dsdouban/book/'+str(book_id)+'/details/')

    
# class CommentUpdateModelForm(forms.ModelForm):
#     class Meta:
#         model = models.Comments
#         # fields = "__all__"
#         fields = ['comment']
        
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # 循环ModelForm中的所有字段，给每个字段的插件设置
#         for name, field in self.fields.items():
#             field.widget.attrs.update = {
#                 "class": "form-control",
#                 "placeholder": field.label
#             }

def comment_update(request, nid):
    row_obj = models.Comments.objects.filter(comment_id=nid).first()
    book_obj = models.Book.objects.filter(book_id=row_obj.book_id).first()
    if request.method == "GET":
        form = CommentModelForm(instance=row_obj)
        return render(request, 'comment_update.html', {'form': form}) 
    
    comment_data = request.POST.copy()
    form = CommentModelForm(instance=row_obj, data=comment_data)
    if form.is_valid():
        form.instance.submission_time = timezone.now() 
        form.save()
        return redirect('/dsdouban/book/'+str(book_obj.book_id)+'/details/')

    return render(request, 'comment_update.html', {'form': form, 'title':"修改评论"}) 