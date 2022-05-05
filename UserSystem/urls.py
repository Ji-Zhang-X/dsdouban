from .views import account, book_view, user_order
from django.urls import path, include

urlpatterns = [
    # 用户登录与注册
    path('', account.begin),
    path('register/', account.register),
    path('login/', account.login),
    path('logout/', account.logout),
    
    # 这里nid是book_id
    path('book/list/', book_view.book_list),
    path('book/<int:nid>/details/',book_view.book_details),
    path('book/<int:nid>/add_comment/',book_view.add_comment),
    path('book/<int:nid>/add_book_to_unsubmitted_order_list/',user_order.add_book_to_unsubmitted_order_list),
    
    # 这里nid是user_id
    path('order/unsubmitted_order/', user_order.show_unsubmitted_order),
    path('order/<int:nid>/edit_unsubmitted_order/', user_order.edit_unsubmitted_order),
    path('order/<int:nid>/edit_unsubmitted_order_list/', user_order.edit_unsubmitted_order_list),
    path('order/<int:nid>/submitted_orders/', user_order.show_submitted_orders),
    
    # 这里用于测试
    path('test',book_view.test),


]
