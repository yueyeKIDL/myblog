from django.core.paginator import Paginator
from django.shortcuts import render_to_response, get_object_or_404, render

from comment.forms import CommentForm
from comment.models import Comment
from read_statistics import utils
from .models import *


# Create your views here.
def get_blog_list_common_data(request, blogs_all_list):
    paginator = Paginator(blogs_all_list, 5)
    page_num = request.GET.get('page', 1)
    page_of_blogs = paginator.get_page(page_num)
    blogs_current_page = page_of_blogs.object_list
    blog_types = BlogType.objects.all()
    current_page_num = page_of_blogs.number
    page_range = [(current_page_num + i) for i in range(-2, 3)
                  if min(paginator.page_range) <= (current_page_num + i) <= max(paginator.page_range)]

    if page_of_blogs.number - 1 > 3:
        page_range.insert(0, '...')

    if page_of_blogs.number + 3 < paginator.num_pages:
        page_range.append('...')

    if 1 not in page_range:
        page_range.insert(0, 1)

    if paginator.num_pages not in page_range:
        page_range.append(paginator.num_pages)

    blog_dates = Blog.objects.dates('created_time', 'month', order='DESC')
    blog_date_dict = {}
    for blog_date in blog_dates:
        blog_date_count = Blog.objects.filter(created_time__year=blog_date.year,
                                              created_time__month=blog_date.month).count()
        blog_date_dict[blog_date] = blog_date_count
    return locals()


def blog_list(request):
    blogs_all_list = Blog.objects.all()
    context = get_blog_list_common_data(request, blogs_all_list)
    return render_to_response('blog/blog_list.html', context)


def blog_detail(request, blog_pk):
    blog = get_object_or_404(Blog, pk=blog_pk)
    read_cookie_key = utils.read_statistics_once_read(request, blog)

    # 评论内容
    blog_content_type = ContentType.objects.get_for_model(blog)
    comments = Comment.objects.filter(content_type=blog_content_type, object_id=blog_pk)

    # 模板评论hidden表单
    data = dict()
    data['content_type'] = blog_content_type
    data['object_id'] = blog_pk
    comment_form = CommentForm(initial=data)

    previous_blog = Blog.objects.filter(created_time__gt=blog.created_time).last()
    next_blog = Blog.objects.filter(created_time__lt=blog.created_time).first()
    response = render(request, 'blog/blog_detail.html', locals())
    response.set_cookie(read_cookie_key, 'true')
    return response


def blogs_with_type(request, blog_type_pk):
    blog_type = get_object_or_404(BlogType, pk=blog_type_pk)
    blogs_all_list = Blog.objects.filter(blog_type=blog_type)
    context = get_blog_list_common_data(request, blogs_all_list)
    return render_to_response('blog/blogs_with_type.html', context)


def blogs_with_date(request, year, month):
    blogs_all_list = Blog.objects.filter(created_time__year=year, created_time__month=month)
    context = get_blog_list_common_data(request, blogs_all_list)
    return render_to_response('blog/blogs_with_date.html', context)
