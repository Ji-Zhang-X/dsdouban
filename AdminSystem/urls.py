from .views import admin_view, book_view, account, user_view, order_view, author_view, press_view, logistics_view
from django.urls import path, include

urlpatterns = [
    path('', book_view.book_list),
    # 书籍的管理
    path('book/list/', book_view.book_list),
    path('book/add/', book_view.book_add),
    path('book/<int:nid>/edit/',book_view.book_edit),
    path('book/<int:nid>/delete/',book_view.book_delete),
    path('book/<int:nid>/details/',book_view.book_details),
    
    # # 作者的管理
    path('author/list/', author_view.author_list),
    path('author/add/', author_view.author_add),
    path('author/<int:nid>/edit/',author_view.author_edit),
    path('author/<int:nid>/delete/',author_view.author_delete),
    
    # 出版社的管理
    path('press/list/', press_view.press_list),
    path('press/add/', press_view.press_add),
    path('press/<int:nid>/edit/',press_view.press_edit),
    path('press/<int:nid>/delete/',press_view.press_delete),
    
    # # 物流的管理
    # path('logistics/list/', logistics_view.logistics_list),
    # path('logistics/add/', logistics_view.logistics_add),
    # path('logistics/<int:nid>/edit/',logistics_view.logistics_edit),
    # path('logistics/<int:nid>/delete/',logistics_view.logistics_delete),
    # path('logistics/<int:nid>/details/',logistics_view.logistics_details),
    
    # 订单的管理
    path('order/list/', order_view.order_list),
    path('order/<int:nid>/details/', order_view.order_details),
    path('order/<int:nid>/delete/', order_view.order_delete),
    path('order/<int:nid>/edit/', order_view.edit_order),

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
