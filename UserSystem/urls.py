from .views import account, book_view
from django.urls import path, include

urlpatterns = [
    # 用户登录与注册
    path('', account.home),
    path('register/', account.register),
    path('login/', account.login),
    path('logout/', account.logout),
    
    path('book/list/', book_view.book_list),
    path('book/<int:nid>/details/',book_view.book_details),
    path('book/<int:nid>/add_comment/',book_view.add_comment),

]
