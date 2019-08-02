import datetime

from django.db.models import Sum

from blog.models import Blog
from read_statistics.models import *


def read_statistics_once_read(request, obj):
    content_type = ContentType.objects.get_for_model(obj.__class__)
    key = '{}_{}_read'.format(content_type.model, obj.pk)
    # if not request.COOKIES.get(key):
        # 点击后总阅读数+1
    if ReadNum.objects.filter(content_type=content_type, object_id=obj.pk).count():
        rd = ReadNum.objects.get(content_type=content_type, object_id=obj.pk)
    else:
        rd = ReadNum(content_type=content_type, object_id=obj.pk)
    rd.read_num += 1
    rd.save()

    # 每日阅读数+1
    date = timezone.now().date()
    if ReadDetail.objects.filter(content_type=content_type, object_id=obj.pk, date=date).count():
        rdl = ReadDetail.objects.get(content_type=content_type, object_id=obj.pk, date=date)
    else:
        rdl = ReadDetail(content_type=content_type, object_id=obj.pk, date=date)
    rdl.read_num += 1
    rdl.save()

    return key


def get_seven_days_read_data(content_type):
    today = timezone.now().date()
    dates = []
    read_nums = []
    for i in range(7, 0, -1):
        date = today - datetime.timedelta(days=i)
        dates.append(date.strftime('%m/%d'))
        read_details = ReadDetail.objects.filter(content_type=content_type, date=date)
        result = read_details.aggregate(read_num_sum=Sum('read_num'))
        read_nums.append(result['read_num_sum'] or 0)
    return dates, read_nums


def get_today_hot_data(content_type):
    today = timezone.now().date()
    read_details = ReadDetail.objects.filter(content_type=content_type, date=today).order_by('-read_num')
    return read_details[:7]


def get_yesterday_hot_data(content_type):
    today = timezone.now().date()
    yesterday = today - datetime.timedelta(days=1)
    read_details = ReadDetail.objects.filter(content_type=content_type, date=yesterday).order_by('-read_num')
    return read_details[:7]


def get_7_days_hot_data():
    today = timezone.now().date()
    date = today - datetime.timedelta(days=7)
    blogs = Blog.objects.filter(read_details__date__gte=date, read_details__date__lt=today) \
        .values('id', 'title') \
        .annotate(read_num_sum=Sum('read_details__read_num')) \
        .order_by('-read_num_sum')
    return blogs[:7]
