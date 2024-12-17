from django.shortcuts import redirect, render
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate, login
from django.http import HttpResponse

def register_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid(): # Validate the form before saving it.
            form.save()
        else:
            # If there are any errors in the form, render the same form again to display validation errors.
            return render(request,'register.html', {'form': form})

    form = UserCreationForm()
    content = {'form': form}
    return render(request, 'register.html', content)

def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user_details = User.objects.get(username = username)
            user = authenticate(request, username=username, password=password) # Check the username and password
            if user is not None:
                login(request, user) # Login the user and return Http response.
                return HttpResponse("Login Success")
            else:
                return render(request, 'login.html', {'message': 'Invalid Credentials'})
        except ObjectDoesNotExist:
            return render(request,'login.html', {'message': 'User does not exist'})

    context = {}
    return render(request,'login.html', context=context)