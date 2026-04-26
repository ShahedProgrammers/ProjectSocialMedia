from django.shortcuts import render , redirect
from django.db import DatabaseError
from .Function_sql import call_procedure
from .decorators import login_required

def register_view(request):
    if request.method == 'POST' :
        email = request.POST.get('email' , '').strip()
        username = request.POST.get('username' , '').strip()
        password = request.POST.get('password' , '')
        
        if not email or not username or not password:
            return render(request, 'register/register.html', {
                'error': 'همه فیلدها الزامی هستند.'
            })
            
        try:
           result = call_procedure('sp_register_user' , [email , username , password]) 
           if result :
               user_id = result[0][0]
               request.session['user_id'] = user_id
               request.session['username'] = username
               return redirect('home')
        except DatabaseError as error :
            error_text = str(error)
            return render(request , 'register/register.html' , {'error': error_text})
    return render(request , 'register/register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        try:
            result = call_procedure('sp_login_user', [username, password])
            if result:
                user_id = result[0][0]
                request.session['user_id'] = user_id
                request.session['username'] = username
                return redirect('home')
        except DatabaseError as e:
            return render(request, 'login/login.html', {'error': 'نام کاربری یا رمز عبور اشتباه است.'})

    return render(request, 'login/login.html')

def logout_view(request) :
    request.session.flush()
    return redirect('login')

@login_required

def home_required(request) :
    username = request.session.get('username', 'کاربر')
    return render(request , 'home/index.html' , {'username' : username})