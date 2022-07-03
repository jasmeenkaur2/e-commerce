from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.core.mail import EmailMultiAlternatives
from django.db.models import Sum
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from .models import Contact

# Create your views here.
from django.urls import reverse_lazy
from django.views.generic import CreateView

from bookshop.forms import RegisterForm, LoginForm
from bookshop.models import Category, Product, SubCategory, Cart, Order, OrderDetails
from web01 import settings


def myindex(request):
    category_data = Category.objects.all()
    featured_productsdata = Product.objects.filter(featured_product=True)
    new_arrivals = Product.objects.all().order_by('-creation_date')[0:2]
    return render(request, "index.html", {"categorydata": category_data, "featuredproducts": featured_productsdata,
                                          "new_arrivals": new_arrivals})


def showsubcategories(request, cid):
    subcategory_data = SubCategory.objects.filter(category=cid)
    return render(request, "subcategories.html", {"subcategorydata": subcategory_data})


def showproductdetail(request, pid):
    productdata = Product.objects.get(id=pid)
    return render(request, "product_detail.html", {"productdata": productdata})

def orderdetails(request, oid):
    orderdetailsdata = OrderDetails.objects.filter(orderno=oid)
    return render(request, "orderdetails.html", {"orderdetailsdata": orderdetailsdata})


def showproducts(request):
    subcategoryid = request.GET.get("subcatid")
    categoryid = request.GET.get("catid")
    products_data = Product.objects.filter(category=categoryid, subcategory=subcategoryid)
    return render(request, "products.html", {"productsdata": products_data})


def mylogin(request):
    return render(request, "login.html")


class mysignup(SuccessMessageMixin, CreateView):
    form_class = RegisterForm
    template_name = 'signup.html'
    success_url = reverse_lazy('signup')
    success_message = 'Signup Successful. You can login now'

    def dispatch(self, *args, **kwargs):
        return super(mysignup, self).dispatch(*args, **kwargs)


def mylogin(request):
    myform = LoginForm(request.POST or None)

    if myform.is_valid():
        username = myform.cleaned_data.get("username")
        userobj = User.objects.get(username__iexact=username)
        myredirect_to = request.POST.get('next')
        login(request, userobj)
        request.session['username'] = username
        request.session['name'] = userobj.first_name
        if myredirect_to:
            return redirect(myredirect_to)
        else:
            return HttpResponseRedirect(reverse_lazy("myhome"))
    return render(request, "login.html", {"form": myform})


def mylogout(request):
    if request.session["username"]:
        del request.session["username"]
    if request.session["name"]:
        del request.session["name"]
    logout(request)
    return HttpResponseRedirect(reverse_lazy("myhome"))


def addtocart(request):
    pid = int(request.POST.get("pid"))
    price = int(float(request.POST.get("price")))
    qty = int(request.POST.get("qty"))
    totalcost = price*qty
    if not request.session or not request.session.session_key:
        request.session.save()
        SESSION_KEY = request.session.session_key
        request.session["sid"] = SESSION_KEY

    cartdata = Cart.objects.filter(productid=pid, sessionid=request.session["sid"]).first()
    if cartdata is not None:
        cartdata.qty = int(cartdata.qty) + qty
        cartdata.totalcost = int(cartdata.price) * cartdata.qty
        Cart.objects.filter(productid=pid, sessionid=request.session["sid"]).update(qty=cartdata.qty, totalcost=cartdata.totalcost)
    else:
        cartobj = Cart()
        cartobj.productid = Product(id=pid)
        cartobj.price = price
        cartobj.qty = qty
        cartobj.totalcost = totalcost
        cartobj.sessionid = request.session["sid"]
        cartobj.save()
    return HttpResponseRedirect(reverse_lazy("showcart"))

def showcart(request):
    cartdata = Cart.objects.filter(sessionid = request.session["sid"]).select_related("productid")
    cartcount = cartdata.count
    cartsum = Cart.objects.filter(sessionid = request.session["sid"]).aggregate(Sum('totalcost'))
    return render(request, "shopping-cart.html", {"cartdata" : cartdata, "cartcount" : cartcount, "cartsum" : cartsum})

def deletecart(request, id):
    Cart.objects.get(id=id).delete()
    return HttpResponseRedirect(reverse_lazy("showcart"))

@login_required()
def mycheckout(request):
    return render(request, "checkout.html")

@login_required()
def myorder(request):
    orderobj = Order()
    name = request.POST.get("name")
    address = request.POST.get("address")
    phone = request.POST.get("phone")
    email = request.POST.get("email")
    paymentmethod = request.POST.get("paymentmethod")
    orderobj.person_name = name
    orderobj.address = address
    orderobj.phone = phone
    orderobj.email = email
    orderobj.username = User.objects.get(username=request.session["username"])
    orderobj.payment_mode = paymentmethod
    cartsum = Cart.objects.filter(sessionid=request.session["sid"]).aggregate(Sum('totalcost'))

    orderobj.grand_total = cartsum['totalcost__sum']
    orderobj.save()
    orderno = Order.objects.latest('id')


    for cartdata in Cart.objects.filter(sessionid=request.session["sid"]):
        myorderdetailsobj = OrderDetails()
        myorderdetailsobj.orderno = orderno
        myorderdetailsobj.productid = cartdata.productid
        myorderdetailsobj.price = cartdata.price
        myorderdetailsobj.qty = cartdata.qty
        myorderdetailsobj.totalcost = cartdata.totalcost
        myorderdetailsobj.save()

    Cart.objects.filter(sessionid=request.session["sid"]).delete()
    message = EmailMultiAlternatives(
        'New sale at your website',          #Subject
        'You have got a new order',     #Email Body
         to = [' '],  # where you receive the contact emails
         from_email = settings.EMAIL_HOST_USER, reply_to = [''])
    result = message.send(fail_silently=False)
    return render(request, "thanks.html", {"orderno" : orderno, "result" : result})

def previousorders(request):
    orders = Order.objects.filter(username=User.objects.get(username=request.session["username"]))
    orderscount = orders.count
    print(orderscount)
    return render(request, "previous-orders.html", {"porders" : orders, "orderscount" : orderscount})

def contact(request):
  if request.method == "POST":
        contact = Contact()
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        contact.name = name
        contact.email = email
        contact.message = message
        contact.save()

  else:
      contact = Contact()
      args = {'contact':contact}
  return render(request, 'contact.html')