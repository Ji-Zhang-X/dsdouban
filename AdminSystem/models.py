from django.db import models


class Admin(models.Model):
    """ 管理员 """
    username = models.CharField(verbose_name="用户名", max_length=32)
    password = models.CharField(verbose_name="密码", max_length=64)

    def __str__(self):
        return self.username
    class Meta():
        verbose_name = '普通管理员' # 单数时显示内容
        verbose_name_plural = '普通管理员' # 复数时显示内容
    

class Book(models.Model):
    book_id = models.BigIntegerField(primary_key=True)
    title = models.CharField(max_length=45)
    publish_date = models.DateTimeField(blank=True, null=True)
    price_standard = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="标准价格")      
    price_vip = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    score = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True, verbose_name="基础评分")
    score_current = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True, verbose_name="现行评分")
    edition = models.CharField(max_length=45, blank=True, null=True)
    storage = models.IntegerField(blank=True, null=True)
    class_field = models.ForeignKey('BookClass', models.DO_NOTHING, db_column='class_id', blank=True, null=False, default='8')  # Field renamed because it was a Python reserved word.
    press = models.ForeignKey('Press', models.DO_NOTHING, blank=True, null=True, verbose_name="出版社编号")
    introduction = models.CharField(max_length=2000, blank=True, null=True)
    authors = models.ManyToManyField('Author', through='BookAuthor')

    class Meta:
        managed = False
        db_table = 'book'
        indexes = [models.Index(fields=['title']),
                   models.Index(fields=['press']),
                   models.Index(fields=['introduction'])]


class BookClass(models.Model):
    class_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45)
    parent_class = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'book_class'
        indexes = [models.Index(fields=['name']),]
        
    def __str__(self):
        return self.name


class Press(models.Model):
    press_id = models.BigAutoField(primary_key=True, verbose_name="出版社id")
    name = models.CharField(max_length=45)
    contact = models.CharField(max_length=45, blank=True, null=True)
    address = models.CharField(max_length=60, blank=True, null=True)
    tele = models.CharField(max_length=20, blank=True, null=True)
    email = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'press'
        indexes = [models.Index(fields=['name']),]
    
    def __str__(self):
        return self.name


class Author(models.Model):
    author_id = models.BigAutoField(primary_key=True)
    translator_choices = (
        (0, "作者"),
        (1, "译者"),
    )
    is_translator = models.IntegerField(default=0, choices=translator_choices)
    name = models.CharField(max_length=40)
    intro = models.CharField(max_length=800, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'author'
        indexes = [models.Index(fields=['name']),]
        
    def __str__(self):
        return self.name

class BookAuthor(models.Model):
    book = models.OneToOneField(Book, models.DO_NOTHING, primary_key=True)
    author = models.ForeignKey(Author, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'book_author'
        unique_together = (('book', 'author'),)
        indexes = [models.Index(fields=['book','author']),]


class Comments(models.Model):
    comment_id = models.BigIntegerField(primary_key=True)
    book = models.ForeignKey('Book', models.DO_NOTHING)
    user = models.ForeignKey('User', models.DO_NOTHING)
    submission_time = models.DateTimeField(auto_now=True)
    comment = models.CharField(max_length=800)

    class Meta:
        managed = False
        db_table = 'comments'
        unique_together = (('book', 'user', 'submission_time'),)
        indexes = [models.Index(fields=['book','user']),]


class Logistics(models.Model):
    logistics_id = models.AutoField(primary_key=True)
    logistics_name = models.CharField(unique=True, max_length=30)
    logistics_tele = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'logistics'
    
    def __str__(self):
        return self.logistics_name


class Order(models.Model):
    order_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey('User', models.DO_NOTHING)
    submission_time = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, default='未提交')
    """status 其他可选值为已付款,已完成和已取消"""
    logistics = models.ForeignKey(Logistics, models.DO_NOTHING, blank=True, null=True)
    telephone = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=45, blank=True, null=True)
    name = models.CharField(max_length=40)
    vip_choices = (
        (0, "普通用户"),
        (1, 'VIP'),
    )
    is_vip = models.IntegerField(default=0, choices=vip_choices)

    class Meta:
        managed = False
        db_table = 'order'
        indexes = [models.Index(fields=['user','name']),]


class OrderList(models.Model):
    order_list_id = models.BigAutoField(primary_key=True)
    order = models.OneToOneField(Order, models.DO_NOTHING)
    book = models.ForeignKey(Book, models.DO_NOTHING)
    number = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'order_list'
        unique_together = (('order', 'book'),)


class User(models.Model):
    user_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=10, verbose_name='用户名')
    password = models.CharField(max_length=40)
    vip_choices = (
        (0, "普通用户"),
        (1, "VIP"),
    )
    is_vip = models.IntegerField(default=0, choices=vip_choices, verbose_name='会员信息')
    telephone = models.CharField(max_length=15, blank=True, null=True)
    e_mail = models.CharField(max_length=45, blank=True, null=True)
    address = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user'
        verbose_name = '普通用户' # 单数时显示内容
        verbose_name_plural = '普通用户' # 复数时显示内容
        indexes = [models.Index(fields=['name']),]

    def __str__(self):
        return self.name


class Mark(models.Model):
    mark_id = models.BigAutoField(primary_key=True)
    book = models.ForeignKey(Book, models.DO_NOTHING)
    user = models.ForeignKey(User, models.DO_NOTHING)
    marks = models.DecimalField(max_digits=3, decimal_places=1)

    class Meta:
        managed = False
        db_table = 'mark'
        unique_together = (('book', 'user'),)

# class AdminsystemAdmin(models.Model):
#     id = models.BigAutoField(primary_key=True)
#     username = models.CharField(max_length=32)
#     password = models.CharField(max_length=64)

#     class Meta:
#         managed = False
#         db_table = 'adminsystem_admin'

# class AuthGroup(models.Model):
#     name = models.CharField(unique=True, max_length=150)

#     class Meta:
#         managed = False
#         db_table = 'auth_group'


# class AuthGroupPermissions(models.Model):
#     id = models.BigAutoField(primary_key=True)
#     group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
#     permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

#     class Meta:
#         managed = False
#         db_table = 'auth_group_permissions'
#         unique_together = (('group', 'permission'),)


# class AuthPermission(models.Model):
#     name = models.CharField(max_length=255)
#     content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
#     codename = models.CharField(max_length=100)

#     class Meta:
#         managed = False
#         db_table = 'auth_permission'
#         unique_together = (('content_type', 'codename'),)


# class AuthUser(models.Model):
#     password = models.CharField(max_length=128)
#     last_login = models.DateTimeField(blank=True, null=True)
#     is_superuser = models.IntegerField()
#     username = models.CharField(unique=True, max_length=150)
#     first_name = models.CharField(max_length=150)
#     last_name = models.CharField(max_length=150)
#     email = models.CharField(max_length=254)
#     is_staff = models.IntegerField()
#     is_active = models.IntegerField()
#     date_joined = models.DateTimeField()

#     class Meta:
#         managed = False
#         db_table = 'auth_user'


# class AuthUserGroups(models.Model):
#     id = models.BigAutoField(primary_key=True)
#     user = models.ForeignKey(AuthUser, models.DO_NOTHING)
#     group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

#     class Meta:
#         managed = False
#         db_table = 'auth_user_groups'
#         unique_together = (('user', 'group'),)


# class AuthUserUserPermissions(models.Model):
#     id = models.BigAutoField(primary_key=True)
#     user = models.ForeignKey(AuthUser, models.DO_NOTHING)
#     permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

#     class Meta:
#         managed = False
#         db_table = 'auth_user_user_permissions'
#         unique_together = (('user', 'permission'),)

# class DjangoAdminLog(models.Model):
#     action_time = models.DateTimeField()
#     object_id = models.TextField(blank=True, null=True)
#     object_repr = models.CharField(max_length=200)
#     action_flag = models.PositiveSmallIntegerField()
#     change_message = models.TextField()
#     content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)  
#     user = models.ForeignKey(AuthUser, models.DO_NOTHING)

#     class Meta:
#         managed = False
#         db_table = 'django_admin_log'


# class DjangoContentType(models.Model):
#     app_label = models.CharField(max_length=100)
#     model = models.CharField(max_length=100)

#     class Meta:
#         managed = False
#         db_table = 'django_content_type'
#         unique_together = (('app_label', 'model'),)


# class DjangoMigrations(models.Model):
#     id = models.BigAutoField(primary_key=True)
#     app = models.CharField(max_length=255)
#     name = models.CharField(max_length=255)
#     applied = models.DateTimeField()

#     class Meta:
#         managed = False
#         db_table = 'django_migrations'


# class DjangoSession(models.Model):
#     session_key = models.CharField(primary_key=True, max_length=40)
#     session_data = models.TextField()
#     expire_date = models.DateTimeField()

#     class Meta:
#         managed = False
#         db_table = 'django_session'
