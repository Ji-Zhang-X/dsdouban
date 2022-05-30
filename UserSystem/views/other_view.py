import copy
from django import forms
from django.utils import timezone
from django.shortcuts import render, redirect
from AdminSystem.utils.pagination import Pagination

from AdminSystem import models






def author_view(request, nid):
    author_obj = models.Author.objects.filter(author_id=nid).first()
    content = { 'obj':author_obj,
    }
    return render(request, 'user_author_detail.html', content)


def press_view(request, nid):
    press_obj = models.Press.objects.filter(press_id=nid).first()
    content = { 'obj':press_obj,
    }
    return render(request, 'user_press_detail.html', content)