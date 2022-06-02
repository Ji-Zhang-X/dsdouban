from django.contrib import admin
from django import forms
# Register your models here.
from AdminSystem.models import Admin,User
from .utils.encrypt import md5
from . import models

class MyUserForm(forms.ModelForm):
    def clean_password(self):
    # do something that validates your data
        return md5(self.cleaned_data["password"])



class Adminmodel(admin.ModelAdmin):
    form = MyUserForm



class Usermodel(admin.ModelAdmin):
    list_display = ('name','is_vip',)
    list_filter = ('is_vip',)
    search_fields = ('name',)
    list_per_page = 10
    form = MyUserForm

    def delete_model(self, request, obj):
        nid = obj.user_id
        orders = models.Order.objects.filter(user_id=nid)
        for oneorder in orders:
            models.OrderList.objects.filter(order_id=oneorder.order_id).delete()
        orders.delete()
        obj.delete()

    def delete_queryset(self,request, queryset):
        for user in queryset:
            nid = user.user_id
            orders = models.Order.objects.filter(user_id=nid)
            for oneorder in orders:
                models.OrderList.objects.filter(order_id=oneorder.order_id).delete()
            orders.delete()
            user.delete()


admin.site.register(Admin, Adminmodel)
admin.site.register(User,Usermodel)