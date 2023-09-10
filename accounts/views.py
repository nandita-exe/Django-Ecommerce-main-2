from cmath import log
from tkinter import E
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate , login , logout
from django.http import HttpResponseRedirect,HttpResponse
# Create your views here.
from .models import Profile
from products.models import Product, SizeVariant, Coupon, ProductImage
from accounts.models import Cart, CartItems
import razorpay
from django.conf import settings
from datetime import datetime
from base.helpers import save_pdf
from base.emails import send_invoice
# from django.core.urlresolvers import reverse
from django.urls import reverse
from django.contrib.auth.decorators import login_required

def login_page(request):
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user_obj = User.objects.filter(username = email)

        if not user_obj.exists():
            messages.warning(request, 'Account not found.')
            return HttpResponseRedirect(request.path_info)


        if not user_obj[0].profile.is_email_verified:
            messages.warning(request, 'Your account is not verified.')
            return HttpResponseRedirect(request.path_info)

        user_obj = authenticate(username = email , password= password)
        if user_obj:
            login(request , user_obj)
            return redirect('/')

        

        messages.warning(request, 'Invalid credentials')
        return HttpResponseRedirect(request.path_info)


    return render(request ,'accounts/login.html')

# @login
def logout_view(request):
    if request.method=="POST":
        logout(request)
        return redirect('login')
    # logout(request)
    # return redirect(reverse('login'))
    # return HttpResponseRedirect()

def register_page(request):

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        user_obj = User.objects.filter(username = email)

        if user_obj.exists():
            messages.warning(request, 'Email is already taken.')
            return HttpResponseRedirect(request.path_info)

        print(email)

        user_obj = User.objects.create(first_name = first_name , last_name= last_name , email = email , username = email)
        user_obj.set_password(password)
        user_obj.save()

        messages.success(request, 'An email has been sent on your mail.')
        return HttpResponseRedirect(request.path_info)


    return render(request ,'accounts/register.html')




def activate_email(request , email_token):
    try:
        user = Profile.objects.get(email_token= email_token)
        user.is_email_verified = True
        user.save()
        return redirect('/')
    except Exception as e:
        return HttpResponse('Invalid Email token')


@login_required(login_url='login')
def add_to_cart(request, uid):
    variant=request.GET.get('variant')
    quantity = request.GET.get('quantity')
    product=Product.objects.get(uid=uid)
    user = request.user
    cart, _ = Cart.objects.get_or_create(user = user, is_paid=False)
    cart_item= CartItems.objects.create(cart=cart,product=product, )
    print(cart)
    if variant:
        variant=request.GET.get('variant')
        size_variant=SizeVariant.objects.get(size_name= variant)
        cart_item.size_variant=size_variant
        cart_item.save()
        print(cart_item)
    if quantity:
        quantity = request.GET.get('quantity')
        cart_item.quantity=quantity
        cart_item.save()
        print(cart_item)
    # print('done')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def update_cart_item(request, uid):
    quantity = request.GET.get('quantity')
    # product=Product.objects.get(uid=uid)
    cart_item = CartItems.objects.get(uid=uid)
    if quantity:
        quantity = request.GET.get('quantity')
        cart_item.quantity=quantity
        cart_item.save()
        print(cart_item)
    context={'cart_item':cart_item}
    return HttpResponseRedirect(request.META['HTTP_REFERER'])
    # return render(request,'accounts/update.html', context=context)


def remove_cart_item(request, uid):
    try:
        cart_item = CartItems.objects.get(uid=uid)
        cart_item.delete()
    except Exception as e:
        print(e)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

# def remove_cart_item(request, cart_item_uid):
#     try: 
#         cart_item=CartItems.objects.get(uid=cart_item_uid)
#         cart_item.delete()
#     except Exception as e: 
#         return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def cart(request):
    cart_obj=None
    try:
        cart_obj = Cart.objects.get(is_paid=False, user=request.user)
    except Exception as e:
        print(e)
    if request.method == 'POST':
        
        coupon = request.POST.get('coupon')
        coupon_obj = Coupon.objects.filter(coupon_code__exact=coupon)

        if not coupon_obj.exists():
            messages.warning(request, 'Invalid coupon code.')
            return HttpResponseRedirect(request.META['HTTP_REFERER'])

        if cart_obj.coupon:
            messages.warning(request, 'Coupon already exists.')
            return HttpResponseRedirect(request.META['HTTP_REFERER'])

        if coupon_obj[0].is_expired:
            messages.warning(request, 'Coupon code expired.')
            return HttpResponseRedirect(request.META['HTTP_REFERER'])

        if cart_obj.get_cart_total() < coupon_obj[0].minimum_amount:
            messages.warning(
                request, f'Amount should be greater than {coupon_obj.minimum_amount}')
            return HttpResponseRedirect(request.META['HTTP_REFERER'])

        cart_obj.coupon = coupon_obj[0]
        cart_obj.save()

        messages.success(request, f'Coupon applied.')
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    if cart_obj:
        client = razorpay.Client(auth=(settings.KEY, settings.SECRET))
        payment=client.order.create({'amount': cart_obj.get_cart_total()*100, 'currency':"INR", 'payment_capture':1})
        
        cart_obj.razor_pay_order_id=payment['id']
        cart_obj.save()
        print('*****')
        print(payment)
        print("+++++")
    else:
        payment=None
    context = {'cart': cart_obj, 'payment': payment}
    return render(request, 'accounts/cart.html', context)
    # context={'cart': Cart.objects.filter(is_paid=False, user=request.user)}
    # return render(request, 'accounts/cart.html', context)




def remove_coupon(request, cart_id):
    cart = Cart.objects.get(uid=cart_id)
    cart.coupon = None
    cart.save()

    messages.success(request, f'Coupon applied.')
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


def success (request):
    order_id = request.GET.get('order_id') 
    # payment_method = request.GET.get('') 
    cart= Cart.objects.get(razor_pay_order_id= order_id)
    cart.is_paid = True 
    cart.order_date=datetime.now()
    cart.save()
    data={'user':cart.user, 'id':order_id, 'order_date': str(cart.order_date), 'description':'T shirt', 'amount': cart.get_cart_total()}
    print(data)
    file_name, success = save_pdf(data)
    if success:

        print(f"PDF file '{file_name}.pdf' successfully generated.")
        file_path = f"public/static/{file_name}.pdf"
        print(str(cart.user))
        send_invoice(email_id=str(cart.user), file_path=file_path)

    else:
        print("PDF generation failed.")
    





    return HttpResponse('Payment Success')