from django.shortcuts import render, redirect
from .. import models
from django import forms

from django import forms
from django.core.exceptions import ValidationError
from ..utils.bootstrap import BootStrapModelForm
from ..utils.encrypt import md5


class UserModelForm(BootStrapModelForm):
    confirm_password = forms.CharField(
        label="确认密码",
        widget=forms.PasswordInput(render_value=True)
    )

    class Meta:
        model = models.User
        fields = "__all__"
        # fields = ["name", 'password', "confirm_password"]
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


class UserEditModelForm(BootStrapModelForm):
    class Meta:
        model = models.User
        fields = ['name']


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

# 用户管理
def user_list(request):
    query_set = models.User.objects.all()
    return render(request, 'user_list.html',{"queryset": query_set})


def user_add(request):
    """ 添加用户 """
    title = "新建用户"
    if request.method == "GET":
        form = UserModelForm()
        return render(request, 'change.html', {'form': form, "title": title})
    form = UserModelForm(data=request.POST)
    if form.is_valid():
        form.save()
        return redirect('/manager/user/list/')

    return render(request, 'change.html', {'form': form, "title": title})


def user_edit(request, nid):
    """ 编辑用户 """
    # 对象 / None
    row_object = models.User.objects.filter(user_id=nid).first()
    if not row_object:
        # return render(request, 'error.html', {"msg": "数据不存在"})
        return redirect('/manager/user/list/')

    title = "编辑用户"
    if request.method == "GET":
        form = UserEditModelForm(instance=row_object)
        return render(request, 'change.html', {"form": form, "title": title})

    form = UserEditModelForm(data=request.POST, instance=row_object)
    if form.is_valid():
        form.save()
        return redirect('/manager/user/list/')
    return render(request, 'change.html', {"form": form, "title": title})


def user_delete(request, nid):
    """ 删除用户 """
    models.User.objects.filter(user_id=nid).delete()
    return redirect('/manager/user/list/')


def user_reset(request, nid):
    """ 重置密码 """
    # 对象 / None
    row_object = models.User.objects.filter(user_id=nid).first()
    if not row_object:
        return redirect('/manager/user/list/')

    title = "重置密码 - {}".format(row_object.username)

    if request.method == "GET":
        form = UserResetModelForm()
        return render(request, 'change.html', {"form": form, "title": title})

    form = UserResetModelForm(data=request.POST, instance=row_object)
    if form.is_valid():
        form.save()
        return redirect('/manager/user/list/')
    return render(request, 'change.html', {"form": form, "title": title})
