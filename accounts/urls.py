from django.urls import path
from accounts.views import login_page,register_page ,logout, activate_email, cart, add_to_cart, remove_cart_item, remove_coupon, success, update_cart_item
from django.views.decorators.http import require_POST
from django.conf import settings
# from products.views import add_to_cart
from django.contrib.auth.views import LogoutView
urlpatterns = [
   path('login/' , login_page , name="login" ),
   path('register/' , register_page , name="register"),
   # path('logout/' , logout , name="logout"),
   path('logout/', LogoutView.as_view(next_page=settings.LOGOUT_REDIRECT_URL), name='logout'),
   # path('logout/', require_POST(logout), name='logout'),
   path('activate/<email_token>/' , activate_email , name="activate_email"),
   path('cart/', cart, name="cart"),
   path('add-to-cart/<uid>/', add_to_cart, name="add_to_cart"),
   path('update_cart_item/<uid>/', update_cart_item, name="update_cart_item"),
   path('remove_cart_item/<uid>/', remove_cart_item, name='remove_cart_item'),
   path('remove_coupon/<cart_id>/', remove_coupon, name='remove_coupon'),
   # path('update_cart/<int:uid>/<str:action>/', update_cart, name='update_cart'),
   path('success/', success, name="success")
]
