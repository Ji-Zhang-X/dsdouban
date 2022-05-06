from .views import admin_view, book_view, account, user_view, order_view
from django.urls import path, include

urlpatterns = [
    path('', book_view.book_list),
    # 书籍的管理
    path('book/list/', book_view.book_list),
    path('book/add/', book_view.book_add),
    path('book/<int:nid>/edit/',book_view.book_edit),
    path('book/<int:nid>/delete/',book_view.book_delete),
    path('book/<int:nid>/details/',book_view.book_details),

    # 订单的管理
    path('order/list/', order_view.order_list),
    path('order/<int:nid>/details/', order_view.order_details),
    path('order/<int:nid>/delete/', order_view.order_delete),

    path('orderlist/<int:nid>/delete/', order_view.order_list_delete),
    path('orderlist/<int:nid>/edit/', order_view.edit_order_list),

    # 评论的管理
    path('comment/<int:nid>/<int:book_id>/delete/',book_view.comment_delete),
    
    # 管理员的管理
    path('admin/list/', admin_view.admin_list),
    path('admin/add/', admin_view.admin_add),
    path('admin/<int:nid>/edit/', admin_view.admin_edit),
    path('admin/<int:nid>/delete/', admin_view.admin_delete),
    path('admin/<int:nid>/reset/', admin_view.admin_reset),

    # 用户的管理
    path('user/list/', user_view.user_list),
    path('user/add/', user_view.user_add),
    path('user/<int:nid>/edit/', user_view.user_edit),
    path('user/<int:nid>/delete/', user_view.user_delete),
    path('user/<int:nid>/reset/', user_view.user_reset),
    
    # 管理员登录
    path('login/', account.login),
    path('logout/', account.logout)
]
