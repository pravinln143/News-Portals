from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView, LogoutView
from news.views import (
    HomeView, ArticleDetailView,  news_like, 
    CommentView, PublishNewsView, BannerView, verify_payment, payment_success, 
    RazorpayPaymentView, handlelogin, handlelogout, signup, ActivateAccountView
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='homepage'),
    path('article/<int:pk>/', ArticleDetailView.as_view(), name='article-detail'),
    path('article/<int:pk>/like/', news_like, name='news-like'),
    path('article/<int:pk>/comment/', CommentView.as_view(), name='article-comment'),
    path('login/', handlelogin, name='login'),
    path('logout/', handlelogout, name='logout'),
    path('signup/', signup, name='signup'),
    path('activate/<uidb64>/<token>/', ActivateAccountView.as_view(), name='activate'),
    path('publish-news/', PublishNewsView.as_view(), name='publish_news'),
    path('banner/', BannerView.as_view(), name='banner_form'),
    path('verify-payment/', verify_payment, name='verify_payment'),
    path('payment-success/', payment_success, name='payment_success'),
    path('razorpay_payment/', RazorpayPaymentView.as_view(), name='razorpay_payment'),
   
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
