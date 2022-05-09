from .views import account, book_view, user_order
from django.urls import path, include

urlpatterns = [
    # 用户登录与注册
    path('', account.begin),
    path('register/', account.register),
    path('login/', account.login),
    path('logout/', account.logout),
    path('user_details/', account.user_details),
    path('edit_user_details/', account.edit_user_details),
    
    # 图书的查看
    # 这里nid是book_id
    path('book/list/', book_view.book_list),
    path('book/<int:nid>/details/',book_view.book_details),
    path('book/<int:nid>/add_book_to_unsubmitted_order_list/',user_order.add_book_to_unsubmitted_order_list),
    
    # 订单的管理
    # 这里nid是user_id
    path('order/unsubmitted_order/', user_order.show_unsubmitted_order),
    path('order/submitted_orders/', user_order.show_submitted_orders),
    path('order/submit_unsubmitted_order/', user_order.submit_unsubmitted_order),
    path('order/<int:nid>/edit_unsubmitted_order/', user_order.edit_unsubmitted_order),
    
    #这里nid是order_id
    path('order/<int:nid>/detail_order/', user_order.show_submitted_order_details),
    path('order/<int:nid>/edit_order/', user_order.edit_submitted_order),
    path('order/<int:nid>/finish_order/', user_order.finish_submitted_order),
    path('order/<int:nid>/cancel_order/', user_order.cancel_submitted_order),


    # 这里nid是order_list_id
    path('order/<int:nid>/edit_unsubmitted_order_list/', user_order.edit_unsubmitted_order_list),
    path('order/<int:nid>/delete_unsubmitted_order_list/', user_order.delete_unsubmitted_order_list),
    
]
