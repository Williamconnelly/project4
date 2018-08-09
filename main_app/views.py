from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Item, Profile
from django.contrib import messages 
from .forms import LoginForm, SignupForm, SellForm, ProfileUpdateForm
import cloudinary.uploader
import cloudinary.api
import requests
import stripe
from django.db.models import Sum
from decimal import Decimal
stripe.api_key = getattr(settings, "STRIPE_SECRET_KEY", None)
public_key = getattr(settings, "STRIPE_PUBLISHABLE_KEY", None)

# Create your views here.
def index(request):
	return render(request, 'index.html', {'key': public_key})

def market(request):
	items = Item.objects.all()
	return render(request, 'market.html', {"items": items})

def checkout(request):
	print('CHECKOUT', request)

	if(request.method == "POST"):
		charge = stripe.Charge.create(
			amount=100,
			currency="usd",
			source=request.POST['stripeToken']
		)
		return HttpResponseRedirect('/')

def login_view(request):
	if(request.method == 'POST'):
		form = LoginForm(request.POST)
		if(form.is_valid()):
			u = form.cleaned_data['username']
			p = form.cleaned_data['password']
			user = authenticate(username=u, password=p)
			if (user is not None):
				if (user.is_active):
					login(request, user)
					print("LOGGED In")
					return HttpResponseRedirect('/')
				else:
					print("Account Disabled")
					return HttpResponseRedirect('/login/')
			else:
				return HttpResponseRedirect('/login/')
				print("Username and/or password is incorrect")
	else:
		form = LoginForm()
		return render(request, 'login.html', {'form': form})

def signup_view(request):
	print("HIT SIGNUP ROUTE")
	if(request.method == 'POST'):
		print("REQUEST WAS POST")
		form = SignupForm(request.POST)
		if form.is_valid():
			print("FORM WAS VALID")
			form.save()
			u = form.cleaned_data.get('username')
			p = form.cleaned_data.get('password1')
			user = authenticate(username=u, password=p)
			login(request, user)
			print("SIGNED UP")
			return HttpResponseRedirect('/')
		else: 
			return HttpResponseRedirect("/")
			print("Invalid Information")
	else:
		form = SignupForm()
		return render(request, "signup.html", {"form": form})

def logout_view(request):
	logout(request)
	return HttpResponseRedirect('/')

def show_item(request, item_id):
	item = Item.objects.get(id=item_id)
	return render(request, 'show.html', {'item': item})

@login_required
def post_item(request):
	form = SellForm(request.POST, request.FILES)
	if(form.is_valid()):
		item = form.save(commit=False)
		item.user = request.user
		item.save()
		return HttpResponseRedirect('/')
	else:
		return HttpResponseRedirect('/sell/')

@login_required
def profile_update(request):
	return render(request, 'profile_update.html', {'user': request.user, 'form': ProfileUpdateForm})

@login_required
def profile(request):
	try:
		profile = Profile.objects.get(user=request.user)
		return render(request, 'profile.html', {'user': request.user, 'profile': profile})
	except:
		print('NO PROFILE')
		return HttpResponseRedirect('/profile/update/')

@login_required
def post_profile(request):
	form = ProfileUpdateForm(request.POST, request.FILES)
	if(form.is_valid()):
		print("######ITS VALID")
		profile, created = Profile.objects.update_or_create(user_id=request.user.id, defaults={**form.cleaned_data, 'user': request.user})
		return HttpResponseRedirect('/profile/')
	else:
		print('NOT VALID')
		return HttpResponseRedirect('/profile/update')




def charity(request):
	return render(request, 'charity.html')

@login_required
def sell(request):
	return render(request, 'sell.html', {'form': SellForm})

@login_required
def cart(request):
	# Get all items
	cart = Item.objects.all()
	subtotal = Item.objects.aggregate(Sum('price'))
	charity_sum = 0
	for item in cart:
		charity_sum += item.price * item.charity_percent
	# Total percentage of cart going to charity
	percentage_to_charity = Decimal(charity_sum / subtotal["price__sum"])
	percentage_to_charity = round(percentage_to_charity, 2)
	# Total dollar value of cart going to charity
	total_to_charity = round(charity_sum / 100, 2)
	return render(request, "cart.html", {
		"items": cart, 
		"subtotal": subtotal["price__sum"],
		"percentage_to_charity": percentage_to_charity,
		"total_to_charity": total_to_charity
	})