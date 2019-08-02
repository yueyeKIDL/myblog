from django.contrib import auth
from django.core.cache import cache
from django.shortcuts import render_to_response, render, reverse, redirect

from blog.models import *
from read_statistics.utils import get_seven_days_read_data, get_today_hot_data, get_yesterday_hot_data, \
    get_7_days_hot_data
from .forms import *


# Create your views here.


def home(request):
    test_all = ContentType.objects.all()
    content_type = ContentType.objects.get_for_model(Blog)
    dates, read_nums = get_seven_days_read_data(content_type=content_type)
    today_hot_dates = get_today_hot_data(content_type)
    yesterday_hot_dates = get_yesterday_hot_data(content_type)

    if not cache.get('cache_7_hot_days'):
        hot_data_for_7_days = get_7_days_hot_data()
        cache.set('cache_7_hot_days', hot_data_for_7_days, 60 * 60)
    else:
        hot_data_for_7_days = cache.get('cache_7_hot_days')
    return render_to_response('home.html', locals())


def login(request):
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            user = auth.authenticate(request, username=username, password=password)
            if user is not None:
                auth.login(request, user)
                return redirect(cache.get('from'))
            else:
                login_form.add_error(None, '用户名或密码不正确')
    else:
        login_form = LoginForm()
        target_url = request.GET.get('from', reverse('home'))
        cache.set('from', target_url, 60 * 10)
    return render(request, 'login.html', locals())


def register(request):
    if request.method == 'POST':
        reg_form = RegForm(request.POST)
        if reg_form.is_valid():
            username = reg_form.cleaned_data['username']
            email = reg_form.cleaned_data['email']
            password = reg_form.cleaned_data['password']
            user = User.objects.create_user(username, email, password)
            user.save()
            request.user.is_authenticated
            user = auth.authenticate(request, username=username, password=password)
            auth.login(request, user)
            return redirect(cache.get('from'))
    else:
        reg_form = RegForm()
        target_url = request.GET.get('from', reverse('home'))
        cache.set('from', target_url, 60 * 10)
    return render(request, 'register.html', locals())
