from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render , redirect
from django.db import DatabaseError
from .Function_sql import call_procedure , fetch_all , fetch_one
from .decorators import login_required
import base64
import os
import uuid

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

# فاز چهارم پروژه با درست کردن پنل انتشار پست
# قابلیت انتشار پست با عکس یا ویدیو و متن
# قابلیت ویرایش پست
# قابلیت حذف پست
def _database_error_message(error):
    return str(error).split("MESSAGE_TEXT =")[-1].strip() if "MESSAGE_TEXT =" in str(error) else str(error)


def _normalize_tags(tags_text):
    tags = []
    for tag in tags_text.replace('\n', ',').split(','):
        cleaned = tag.strip().lstrip('#')
        if cleaned and cleaned not in tags:
            tags.append(cleaned)
    return ','.join(tags)


def _normalize_datetime(datetime_value):
    if not datetime_value:
        return None
    value = datetime_value.strip()
    if not value:
        return None
    return value.replace('T', ' ')


def _save_post_media(uploaded_file):
    if not uploaded_file:
        return None, 'text'

    content_type = uploaded_file.content_type or ''
    if content_type.startswith('image/'):
        media_type = 'image'
    elif content_type.startswith('video/'):
        media_type = 'video'
    else:
        raise ValueError('فقط فایل عکس یا ویدیو مجاز است.')

    extension = os.path.splitext(uploaded_file.name)[1]
    filename = f"{uuid.uuid4().hex}{extension}"
    storage = FileSystemStorage(location=settings.MEDIA_ROOT / 'posts', base_url=settings.MEDIA_URL + 'posts/')
    saved_name = storage.save(filename, uploaded_file)
    return storage.url(saved_name), media_type


def _get_user_posts(user_id):
    rows = fetch_all(
        """
        SELECT p.PostID, p.Caption, p.MediaURL, p.MediaType, p.CommentsEnabled, p.ScheduledTime
          FROM Posts p
         WHERE p.UserID = %s
         ORDER BY p.PostID DESC
        """,
        [user_id]
    )

    posts = []
    for row in rows:
        posts.append({
            'post_id': row[0],
            'caption': row[1] or '',
            'media_url': row[2],
            'media_type': row[3],
            'comments_enabled': row[4],
            'scheduled_time': row[5],
        })
    return posts


def _get_user_post(user_id, post_id):
    row = fetch_one(
        """
        SELECT PostID, Caption, MediaURL, MediaType, CommentsEnabled, ScheduledTime
          FROM Posts
         WHERE UserID = %s
           AND PostID = %s
        """,
        [user_id, post_id]
    )

    if not row:
        return None

    return {
        'post_id': row[0],
        'caption': row[1] or '',
        'media_url': row[2],
        'media_type': row[3],
        'comments_enabled': row[4],
        'scheduled_time': row[5],
    }


@login_required
def create_post_view(request, post_id=None):
    user_id = request.session.get('user_id')
    editing_post = _get_user_post(user_id, post_id) if post_id else None

    if post_id and not editing_post:
        return redirect('create_post')

    context = {
        'post': editing_post,
        'posts': _get_user_posts(user_id),
    }

    if request.method == 'POST':
        caption = request.POST.get('caption', '').strip()
        comments_enabled = request.POST.get('comments_enabled') == 'on'

        try:
            if editing_post:
                call_procedure(
                    'sp_update_post',
                    [user_id, post_id, caption, comments_enabled]
                )
                return redirect('create_post')

            media_url, media_type = _save_post_media(request.FILES.get('media'))

            if media_type == 'text' and not caption:
                context['error'] = 'متن پست نمی‌تواند خالی باشد.'
                return render(request, 'create-post/create-post.html', context)

            if media_type != 'text' and not media_url:
                context['error'] = 'برای پست عکس یا ویدیو فایل الزامی است.'
                return render(request, 'create-post/create-post.html', context)

            call_procedure(
                'sp_create_post',
                [
                    user_id,
                    caption,
                    media_url,
                    media_type,
                    comments_enabled,
                    _normalize_datetime(request.POST.get('scheduled_time')),
                    _normalize_tags(request.POST.get('tags', ''))
                ]
            )
            return redirect('create_post')

        except ValueError as error:
            context['error'] = str(error)
        except DatabaseError as error:
            context['error'] = _database_error_message(error)

    return render(request, 'create-post/create-post.html', context)


@login_required
def delete_post_view(request, post_id):
    if request.method == 'POST':
        try:
            call_procedure(
                'sp_delete_post',
                [request.session.get('user_id'), post_id]
            )
        except DatabaseError:
            pass

    return redirect('create_post')
