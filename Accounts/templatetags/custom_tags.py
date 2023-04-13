from django.urls import translate_url
from django.template import Library

register = Library()

@register.simple_tag(takes_context=True)
def change_language(context,lang=None,*args,**kwargs):
    request = context.get('request')
    path = request.path
    return translate_url(path,lang)
