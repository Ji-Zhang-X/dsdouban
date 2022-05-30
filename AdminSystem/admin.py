from django.contrib import admin
# Register your models here.
from AdminSystem.models import Admin,User

class Adminmodel(admin.ModelAdmin):
    pass

class Usermodel(admin.ModelAdmin):
    list_display = ('name','is_vip',)
    list_filter = ('is_vip',)
    search_fields = ('name',)
    list_per_page = 10


admin.site.register(Admin, Adminmodel)
admin.site.register(User,Usermodel)