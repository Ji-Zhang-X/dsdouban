## 创建数据库
```
配置如下
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'DSDouBan',
        'USER':'root',
        'PASSWORD':'zhangji20011020',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}
注意需将本地mysql root用户的密码改为如上密码
```
## 导入Dump20220424.sql
注意先登录mysql控制台，再使用source指令，同时source指令需要没有空格和中文的绝对地址
```
mysql -u root -p
source your/path/to/Dump20220424.sql
```

## 将剩余的model注册到数据库中
```
python manage.py makemigrations
python manage.py migrate
```

## 插入管理员和用户数据
```
用sql语句插入两条管理员数据到表Admin中
```

## 跑起来！
```
python manage.py runserver
```
