from io import BytesIO

from django import forms
from django.shortcuts import render, redirect, HttpResponse
from django.core.exceptions import ValidationError


from ..utils.code import check_code
from AdminSystem import models
from ..utils.bootstrap import BootStrapForm, BootStrapModelForm
from ..utils.encrypt import md5
from UserSystem.views import book_view

class LoginForm(BootStrapForm):
    name = forms.CharField(
        label="用户名",
        widget=forms.TextInput,
        required=True
    )
    password = forms.CharField(
        label="密码",
        widget=forms.PasswordInput(render_value=True),
        required=True
    )

    # code = forms.CharField(
    #     label="验证码",
    #     widget=forms.TextInput,
    #     required=True
    # )

    def clean_password(self):
        pwd = self.cleaned_data.get("password")
        return md5(pwd)


def login(request):
    """ 登录 """
    if request.method == "GET":
        form = LoginForm()
        return render(request, 'user_login.html', {'form': form})

    form = LoginForm(data=request.POST)
    if form.is_valid():
        user_object = models.User.objects.filter(**form.cleaned_data).first()
        if not user_object:
            form.add_error("password", "用户名或密码错误")
            # form.add_error("username", "用户名或密码错误")
            return render(request, 'user_login.html', {'form': form})

        # 用户名和密码正确
        # 网站生成随机字符串; 写到用户浏览器的cookie中；在写入到session中；
        request.session["info"] = {'id': user_object.user_id, 'name': user_object.name, 'auth': "user", 'vip' : user_object.is_vip}
        # session可以保存7天
        request.session.set_expiry(60 * 60 * 24 * 7)

        return redirect("/")

    return render(request, 'user_login.html', {'form': form})


def image_code(request):
    """ 生成图片验证码 """

    # 调用pillow函数，生成图片
    img, code_string = check_code()

    # 写入到自己的session中（以便于后续获取验证码再进行校验）
    request.session['image_code'] = code_string
    # 给Session设置60s超时
    request.session.set_expiry(60)

    stream = BytesIO()
    img.save(stream, 'png')
    return HttpResponse(stream.getvalue())


def logout(request):
    """ 注销 """

    request.session.clear()

    return redirect('/dsdouban/login/')

class UserModelForm(BootStrapModelForm):
    confirm_password = forms.CharField(
        label="确认密码",
        widget=forms.PasswordInput(render_value=True)
    )

    class Meta:
        model = models.User
        exclude = ["is_vip"]
        fields = "__all__"
        # fields = ["name", 'password', "confirm_password", "telephone", "e_mail", "address"]
        widgets = {
            "password": forms.PasswordInput(render_value=True)
        }

    def clean_password(self):
        pwd = self.cleaned_data.get("password")
        return md5(pwd)

    def clean_confirm_password(self):
        pwd = self.cleaned_data.get("password")
        confirm = md5(self.cleaned_data.get("confirm_password"))
        if confirm != pwd:
            raise ValidationError("密码不一致")
        # 返回什么，此字段以后保存到数据库就是什么。
        return confirm

def register(request):
    """ 用户注册 """
    title = "用户注册"
    if request.method == "GET":
        form = UserModelForm()
        return render(request, 'register.html', {'form': form, "title": title})
    form = UserModelForm(data=request.POST)
    if form.is_valid():
        form.save()
        return render(request, 'register_success.html')

    return render(request, 'register.html', {'form': form, "title": title})


def begin(request):
    """登录界面"""
    return render(request, 'begin.html')

def home(request):
    """主界面"""
    search_data = request.GET.get('q', "")
    if search_data == '':
        topBooks = ['9787541151200','9787544269155','9787540786038','9787544722803']
        row_object = {}
        extract = {}
        for i,bookID in enumerate(topBooks):
            row_object[i] = models.Book.objects.filter(book_id=bookID).first()
            extract[row_object[i].book_id] = row_object[i].introduction[0:100] + '...'
        context = {
            "row_object": row_object,
            "extract": extract
        }
        return render(request, 'home.html',context)
    return book_view.book_list(request)

def user_details(request):
    """用户信息"""
    info_dict = request.session.get("info")
    current_user = models.User.objects.filter(user_id=info_dict['id']).first()
    return render(request, 'user_details.html', {'user': current_user})

class UserDetailsModelForm(forms.ModelForm):
    class Meta:
        model = models.User
        # fields = "__all__"
        fields = ['name', 'telephone', 'e_mail', 'address']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 循环ModelForm中的所有字段，给每个字段的插件设置
        for name, field in self.fields.items():
            field.widget.attrs = {
                "class": "form-control",
                "placeholder": field.label
            }

def edit_user_details(request):
    """"""
    info_dict = request.session.get("info")
    current_user = models.User.objects.filter(user_id=info_dict['id']).first()
    title = "修改个人信息"
    page_title = '豆丝豆瓣·修改个人信息'    
    label2label = {'Name':'用户名', 'Telephone':'电话', 'E mail':'E-mail', 'Address':'地址'}

    if request.method == "GET":
        form = UserDetailsModelForm()
        return render(request, 'user_change.html', {'form': form, "title": title, "page_title": page_title,'label2label':label2label})
    
    form = UserDetailsModelForm(data=request.POST, instance=current_user)
    if form.is_valid():
        form.save()
        request.session["info"]["name"] = request.POST.get("name")
        request.session.set_expiry(60 * 60 * 24 * 7)
        return redirect('/dsdouban/user_details/')
    
    return render(request, 'user_change.html', {'form': form, "title": title, "page_title": page_title,'label2label':label2label})