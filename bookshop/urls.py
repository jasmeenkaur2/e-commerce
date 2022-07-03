from django.conf.urls.static import static
from django.urls import path

from bookshop import views
from web01 import settings

urlpatterns = [
    path('', views.myindex, name='myhome'),
    path('user-login', views.mylogin, name='login'),
    path('user-logout', views.mylogout, name='logout'),
    path('create-account', views.mysignup.as_view(), name='signup'),
    path('products', views.showproducts, name='products'),
    path('sub-categories/<int:cid>', views.showsubcategories, name='subcategories'),
    path('product-detail/<int:pid>', views.showproductdetail, name='productdetail'),
    path('delete-cart/<int:id>', views.deletecart, name='deletecart'),
    path('add-to-cart', views.addtocart, name='addtocart'),
    path('shopping-cart', views.showcart, name='showcart'),
    path('user-checkout', views.mycheckout, name='checkout'),
    path('order-success', views.myorder, name='order'),
    path('order-details/<int:oid>', views.orderdetails, name='orderdetails'),
    path('my-orders', views.previousorders, name='previousorders'),
    path('contact/', views.contact, name='contact'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)