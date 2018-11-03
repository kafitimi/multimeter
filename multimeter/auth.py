from django.contrib.auth import authenticate, login as django_login
from multimeter.models import Account


def login(request, cleaned_data):
	user = authenticate(request, **cleaned_data)
	if user is None:
		return False
	django_login(request, user)
	return True


def signup(request, cleaned_data):
	username = cleaned_data['username']
	email = cleaned_data['email']
	if Account.objects.filter(username=username) or Account.objects.filter(email=email):
		return False
	user = Account.objects.create_user(**cleaned_data)
	user.save()
	return login(request, cleaned_data)
