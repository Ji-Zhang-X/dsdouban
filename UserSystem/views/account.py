from io import BytesIO
import re
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

    def clean_name(self):
        urname = self.cleaned_data.get("name")
        existing_name = models.User.objects.filter(name=urname).first()
        if existing_name:
            raise ValidationError("用户名已经有人取过了！")
        return urname

    def clean_telephone(self):
        tele = self.cleaned_data.get("telephone")
        if not  re.match('^1[3-9]\d{9}$', tele):
            raise ValidationError("手机号格式错误")
        return tele
    
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
    label2label = {'用户名':'用户名','确认密码':'确认密码','Password':'密码','Telephone':'联系方式','E mail':'电子邮箱', 'Address': '收货地址'}
    if request.method == "GET":
        form = UserModelForm()
        return render(request, 'register.html', {'form': form, "title": title, 'label2label':label2label})
    form = UserModelForm(data=request.POST)
    if form.is_valid():
        form.save()
        return render(request, 'register_success.html')

    return render(request, 'register.html', {'form': form, "title": title, 'label2label':label2label})


def begin(request):
    """登录界面"""
    return render(request, 'begin.html')


def home(request):
    """主界面"""
    search_data = request.GET.get('q', "")
    class_option = request.GET.get('class', "")
    class_field = models.BookClass.objects.filter()
    class_field_dict = {}
    for item in class_field:
        if class_field_dict.get(item.parent_class) == None:
            class_field_dict[item.parent_class] = [item.name]
        else:
            class_field_dict[item.parent_class].append(item.name)

    if search_data == '' and class_option == '': 
        topBooks1 = ['9787541151200','9787544269155','9787540786038','9787544722803']
        topBooks2 = ['9787533962968', '9787220105135','9787567534575','9787220103728']
        # 以上是首页展示的两行图书的id
        row1_object = {}
        row2_object = {}
        extract = {}
        for i,bookID in enumerate(topBooks1):
            row1_object[i] = models.Book.objects.filter(book_id=bookID).first()
            extract[row1_object[i].book_id] = row1_object[i].introduction[0:100] + '...'
        for i,bookID in enumerate(topBooks2):
            row2_object[i] = models.Book.objects.filter(book_id=bookID).first()
            extract[row2_object[i].book_id] = row2_object[i].introduction[0:100] + '...'
        context = {
            "row1_object": row1_object,
            "row2_object": row2_object,
            "extract": extract,
            "class_field_dict": class_field_dict
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

    def clean_name(self):
        urname = self.cleaned_data.get("name")
        existing_name = models.User.objects.filter(name=urname).first()
        if existing_name:
            raise ValidationError("用户名已经有人取过了！")
        return urname

def edit_user_details(request):
    """"""
    info_dict = request.session.get("info")
    current_user = models.User.objects.filter(user_id=info_dict['id']).first()
    title = "修改个人信息"
    page_title = '豆丝豆瓣·修改个人信息'    
    label2label = {'用户名':'用户名', 'Telephone':'电话', 'E mail':'E-mail', 'Address':'地址'}

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

class UserResetModelForm(BootStrapModelForm):
    confirm_password = forms.CharField(
        label="确认密码",
        widget=forms.PasswordInput(render_value=True)
    )

    class Meta:
        model = models.User
        fields = ['password', 'confirm_password']
        widgets = {
            "password": forms.PasswordInput(render_value=True)
        }

    def clean_password(self):
        pwd = self.cleaned_data.get("password")
        md5_pwd = md5(pwd)

        # 去数据库校验当前密码和新输入的密码是否一致
        exists = models.User.objects.filter(user_id=self.instance.pk, password=md5_pwd).exists()
        if exists:
            raise ValidationError("不能与以前的密码相同")

        return md5_pwd

    def clean_confirm_password(self):
        pwd = self.cleaned_data.get("password")
        confirm = md5(self.cleaned_data.get("confirm_password"))
        if confirm != pwd:
            raise ValidationError("密码不一致")
        # 返回什么，此字段以后保存到数据库就是什么。
        return confirm
    
def reset_user_password(request):
    """"""
    info_dict = request.session.get("info")
    current_user = models.User.objects.filter(user_id=info_dict['id']).first()
    title = "修改用户密码"
    page_title = '豆丝豆瓣·修改用户密码'    
    label2label = {'Password':'密码', '确认密码':'确认密码'}

    if request.method == "GET":
        form = UserResetModelForm()
        return render(request, 'user_change.html', {'form': form, "title": title, "page_title": page_title,'label2label':label2label})
    
    form = UserResetModelForm(data=request.POST, instance=current_user)
    if form.is_valid():
        form.save()
        request.session["info"]["name"] = request.POST.get("name")
        request.session.set_expiry(60 * 60 * 24 * 7)
        return redirect('/dsdouban/user_details/')
    
    return render(request, 'user_change.html', {'form': form, "title": title, "page_title": page_title,'label2label':label2label})

def upgrade(request):
    return render(request, 'user_upgrading.html')