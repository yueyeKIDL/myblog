from ckeditor.widgets import CKEditorWidget
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.db.models import ObjectDoesNotExist


class CommentForm(forms.Form):
    content_type = forms.CharField(widget=forms.HiddenInput)
    object_id = forms.IntegerField(widget=forms.HiddenInput)
    text = forms.CharField(label=False, widget=CKEditorWidget(config_name='awesome_ckeditor'))

    # 既得到了user,又不影响form的初始化
    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            self.user = kwargs.pop('user')
        super(CommentForm, self).__init__(*args, **kwargs)

    def clean(self):

        # 判断用户是否登录
        if self.user.is_authenticated:
            self.cleaned_data['user'] = self.user
        else:
            raise forms.ValidationError('用户未登录')

        # 判断评论内容是否为空
        # text = self.cleaned_data['text'].strip()
        # if text == '':
        #     raise forms.ValidationError('评论内容为空')

        object_id = self.cleaned_data['object_id']
        content_type_str = self.cleaned_data['content_type']
        try:
            model_class = ContentType.objects.get(model=content_type_str).model_class()
            model_obj = model_class.objects.get(pk=object_id)
        except ObjectDoesNotExist:
            raise forms.ValidationError('评论对象不存在')
        self.cleaned_data['model_obj'] = model_obj
        return self.cleaned_data
