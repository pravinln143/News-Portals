from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView, FormView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
import razorpay
from .models import News, Banner
from .forms import NewUserForm, CommentForm, NewsForm, BannerForm
from .utils import generate_token
from django.contrib.auth import authenticate, login, logout

class HomeView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["news"] = News.objects.all().order_by("-created_at")
        context["banners"] = Banner.objects.all().order_by("-posted_at")
        return context


class ArticleDetailView(TemplateView):
    template_name = "article_details.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["article"] = get_object_or_404(News, pk=kwargs.get("pk"))
        context["comment_form"] = CommentForm()
        return context


@method_decorator(login_required, name='dispatch')
class CommentView(FormView):
    form_class = CommentForm
    template_name = "article_details.html"

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.posted_by = self.request.user
        comment.article_id = self.kwargs.get("pk")
        comment.save()
        return HttpResponseRedirect(reverse("article-detail", args=[self.kwargs.get("pk")]))


@login_required
def news_like(request, pk):
    news = get_object_or_404(News, pk=pk)

    if news.likes.filter(id=request.user.id).exists():
        news.likes.remove(request.user)
    else:
        news.likes.add(request.user)

    return HttpResponseRedirect(reverse("article-detail", args=[str(pk)]))


@method_decorator(login_required(login_url='login'), name='dispatch')
class PublishNewsView(View):
    def get(self, request):
        form = NewsForm()
        return render(request, 'publish_news.html', {'form': form})

    def post(self, request):
        form = NewsForm(request.POST, request.FILES)
        if form.is_valid():
            news = form.save(commit=False)
            news.author = request.user

            if news.image and news.image_url:
                news.image_url = None
            elif not news.image and not news.image_url:
                form.add_error(None, "Please provide either an image file or an image URL.")
                return render(request, 'publish_news.html', {'form': form})

            news.save()
            form.save_m2m()
            messages.success(request, "News published successfully!")
            return redirect('homepage')

        return render(request, 'publish_news.html', {'form': form})


@method_decorator(login_required(login_url='login'), name='dispatch')
class BannerView(View):
    def get(self, request):
        form = BannerForm()
        return render(request, 'banner_form.html', {'form': form})

    def post(self, request):
        form = BannerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Banner created successfully!")
            return redirect('homepage')
        return render(request, 'banner_form.html', {'form': form})


@csrf_exempt
def verify_payment(request):
    if request.method == "POST":
        payment_id = request.POST.get('razorpay_payment_id', '')
        razorpay_order_id = request.POST.get('razorpay_order_id', '')
        signature = request.POST.get('razorpay_signature', '')

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        try:
            client.utility.verify_payment_signature({
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            })
            return redirect('payment_success')
        except razorpay.errors.SignatureVerificationError:
            return JsonResponse({'status': 'failure'})


def payment_success(request):
    return render(request, 'success.html')


class RazorpayPaymentView(View):
    def get(self, request):
        amount = 500000
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        razorpay_order = client.order.create({
            "amount": amount,
            "currency": "INR",
            "payment_capture": "1"
        })

        context = {
            'razorpay_order_id': razorpay_order['id'],
            'razorpay_merchant_key': settings.RAZORPAY_KEY_ID,
            'amount': amount,
            'currency': 'INR',
        }
        return render(request, 'razorpay_payment.html', context)


def signup(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['pass1']
        confirm_password = request.POST['pass2']

        if password != confirm_password:
            messages.warning(request, "Passwords do not match.")
            return render(request, 'signup.html', {'email': email})

        try:
            if User.objects.filter(username=email).exists():
                messages.info(request, "Email is already taken.")
                return render(request, 'signup.html', {'email': email})

            user = User.objects.create_user(username=email, email=email, password=password)
            user.is_active = False
            user.save()

            email_subject = "Activate Your Account"
            message = render_to_string('activate.html', {
                'user': user,
                'domain': request.get_host(),
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': generate_token.make_token(user),
            })
            email_message = EmailMessage(email_subject, message, settings.EMAIL_HOST_USER, [email])
            email_message.send()

            messages.success(request, "Activate your account by clicking the link sent to your email")
            return redirect('signup')
        
        except IntegrityError:
            messages.error(request, "There was a problem creating your account. Please try again")
            return render(request, 'signup.html', {'email': email})

    return render(request, 'signup.html')


class ActivateAccountView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user and generate_token.check_token(user, token):
            if not user.is_active:
                user.is_active = True
                user.save()
                messages.success(request, "Your account has been activated successfully.")
            else:
                messages.info(request, "Your account is already activated.")
        else:
            messages.error(request, "The activation link is invalid or has expired.")

        return redirect('login')


def handlelogin(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('homepage') 
        else:
            messages.error(request, "Invalid email or password.")
            return render(request, 'login.html', {'error': "Invalid email or password."})
    
    return render(request, "login.html")


def handlelogout(request):
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect('login')