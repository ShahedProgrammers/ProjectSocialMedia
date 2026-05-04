from django.shortcuts import render , redirect
from django.db import DatabaseError
from .Function_sql import call_procedure , fetch_one
from .decorators import login_required
import base64

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
    profile_pic = None

    try:
        result = fetch_one(
            "SELECT ProfilePic FROM Users WHERE UserID=%s",
            [request.session['user_id']]
        )

        if result and result[0]:
            profile_pic = base64.b64encode(bytes(result[0])).decode('utf-8')

    except Exception as e:
        print(f"Error loading profile pic: {e}")

    return render(request, 'home/index.html', {
        'username': username,
        'profile_pic': profile_pic
    })

"""
-----------------------------------------------------------------------------------------------
 فاز سوم پروژه با درست کردن پنل پروفایل 
 قابلیت دیدن صفحه شخصی و ادیت پروفایل و ادیت پسورد و حذف اکانت 
"""
    
@login_required
def profile_view(request):

    user_id = request.session.get('user_id')

    try:
        result = call_procedure('sp_get_user_profile', [user_id])

        if not result:
            return redirect('home')

        user = result[0]

        profile = {
            'user_id': user[0],
            'username': user[1],
            'email': user[2],
            'bio': user[3] if user[3] else '',
            'faceid': user[4]
        }

        pic = fetch_one(
            "SELECT ProfilePic FROM Users WHERE UserID=%s",
            [user_id]
        )

        profile_pic = None
        if pic and pic[0]:
            profile_pic = base64.b64encode(bytes(pic[0])).decode('utf-8')


        return render(request, 'profile/profile.html', {
            'profile': profile,
            'profile_pic': profile_pic,
            
        })

    except DatabaseError:
        return redirect('home')


@login_required
def edit_profile_view(request):

    user_id = request.session.get('user_id')

    if request.method == 'POST':

        bio = request.POST.get('bio', '').strip()
        image = request.FILES.get('profile_pic')

        image_bytes = None
        if image:
            
            image_bytes = image.read()


        try:
            call_procedure(
                'sp_update_user_profile',
                [user_id, bio , image_bytes]
            )

            return redirect('profile')

        except DatabaseError as e:
            return render(request, 'profile/profile.html', {
                'error': str(e)
            })

    return render(request, 'profile/profile.html')

@login_required
def change_password_view(request):

    user_id = request.session.get('user_id')

    if request.method == 'POST':

        current = request.POST.get('current_password')
        new = request.POST.get('new_password')

        try:
            call_procedure(
                'sp_change_password',
                [user_id, current, new]
            )

            return redirect('profile')

        except DatabaseError as e:
            return render(request, 'settings/settings.html', {
                'error': str(e)
            })

    return render(request, 'settings/settings.html')


@login_required
def delete_account_view(request):

    user_id = request.session.get('user_id')

    if request.method == 'POST':

        password = request.POST.get('password')

        try:
            call_procedure(
                'sp_delete_account',
                [user_id, password]
            )

            request.session.flush()

            return redirect('register')

        except DatabaseError as e:
            return render(request, 'settings/settings.html', {
                'error': str(e)
            })

    return render(request, 'settings/settings.html')

@login_required
def settings_view(request):
    user_id = request.session.get('user_id')
    username = request.session.get('username', 'کاربر')
    profile_pic = None

    try:
        result = fetch_one(
            "SELECT ProfilePic FROM Users WHERE UserID=%s",
            [request.session['user_id']]
        )

        if result and result[0]:
            profile_pic = base64.b64encode(bytes(result[0])).decode('utf-8')

    except Exception as e:
        print(f"Error loading profile pic: {e}")

    
    return render(request, 'settings/settings.html' ,  {
        'username': username,
        'profile_pic': profile_pic,
        'user_id' : user_id
    })
