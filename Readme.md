## 1 创建数据库导入数据文件
注意先登录mysql控制台，再使用source指令，同时source指令需要没有空格和中文的绝对地址
```
mysql -u root -p
create schema DSDouBan;
use DSDouBan;
source your/path/to/Dump20220523.sql
```
## 2 配置django中的数据库
```
于文件 DSDouBan\settings.py 第81行数据库配置：
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'DSDouBan',
        'USER':'root',
        'PASSWORD':'your_password',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}
```
## 3 将剩余的model注册到数据库中
```
python manage.py makemigrations
python manage.py migrate
```

## 4 跑起来！
```
python manage.py runserver
```
打开浏览器并访问 http://127.0.0.1:8000/ 即可进入数据库系统。