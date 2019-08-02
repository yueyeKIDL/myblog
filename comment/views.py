from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse
from django.http import JsonResponse

# Create your views here.
from comment.forms import CommentForm
from .models import *


def update_comment(request):

    # 评论后，重定向的页面地址
    referer = request.META.get('HTTP_REFERER', reverse('home'))

    # 为评论即将写入数据库，做好准备姿势(各种数据验证已写在CommentForm中)
    comment_form = CommentForm(request.POST, user=request.user)
    if comment_form.is_valid():

        # 评论写入数据库
        comment = Comment()
        comment.user = comment_form.cleaned_data['user']
        comment.text = comment_form.cleaned_data['text']
        comment.content_object = comment_form.cleaned_data['model_obj']
        comment.save()
        data = {}
        data['status'] = 'SUCCESS'
        data['username'] = comment.user.username
        data['comment_time'] = comment.comment_time.strftime("%Y %m %d %H:%M:%S")
        data['text'] = comment.text
        # return redirect(referer)
    else:
        data = {}
        data['status'] = 'ERROR'
        data['message'] = list(comment_form.errors.values())[0][0]
    return JsonResponse(data)
