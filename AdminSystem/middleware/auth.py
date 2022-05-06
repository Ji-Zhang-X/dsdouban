import re
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import HttpResponse, redirect, render


class AuthMiddleware(MiddlewareMixin):

    def process_request(self, request):
        # 0.排除那些不需要登录就能访问的页面        
        if request.path_info in ["/manager/login/", 
                                 "/manager/logout/",
                                 "/dsdouban/register/", 
                                 "/dsdouban/",
                                 "/dsdouban/login/",
                                 "/dsdouban/warning/",
                                 "/dsdouban/logout/",
                                 "/"]:
            return

        # 1.读取当前访问的用户的session信息，如果登录过，按照用户是user还是admin分类讨论。
        info_dict = request.session.get("info")
        if info_dict:
            if info_dict['auth'] == "admin":
                return
            else:
                if re.match('/dsdouban/*', request.path_info):
                    return
                else:
                    title = "您无管理员权限。"
                    skiplink = "/"
                    print(skiplink)
                    return render(request, 'warning.html', {"title": title, "skiplink": skiplink})

        # 2.没有登录过，重新回到登录页面
        title = "您未登录。"
        skiplink = "/dsdouban/login/"
        return render(request, 'warning.html', {"title": title, "skiplink": skiplink})
