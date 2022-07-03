import datetime

from django import template
from django.template import context

from bookshop.models import Category, Cart

register = template.Library()


@register.simple_tag
def current_time():
    return datetime.datetime.now()


@register.inclusion_tag("fetch_categories.html")
def fetchcategories():
    categorydata = Category.objects.all()
    return {"categorydata" :  categorydata}

# @register.inclusion_tag("cartcount.html")
# def showcartcount():
#     cartdata = Cart.objects.filter(sessionid=context.request.session["sid"]).select_related("productid")
#     cartcount = cartdata.count
#     return {"cartcount" : cartcount}