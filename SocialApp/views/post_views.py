from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.shortcuts import render , redirect
from django.db import DatabaseError
from ..Function_sql import call_procedure , execute , fetch_all , fetch_one
from ..decorators import login_required
import base64
import json
import os
import uuid
from datetime import datetime




def _normalize_media_url(url):
    if not url:
        return url

    value = str(url).strip().replace('\\', '/')
    if value.startswith(('http://', 'https://', '//')):
        return value

    media_prefix = settings.MEDIA_URL.rstrip('/') + '/'

    if value.startswith('/'):
        path = value.lstrip('/')
        if path.lower().startswith('media/'):
            rest = path[6:].lstrip('/')
            if rest and not rest.lower().startswith('posts/'):
                rest = f'posts/{rest}'
            return f'{media_prefix}{rest}'
        return value

    path = value.lstrip('/')
    if path.lower().startswith('media/'):
        rest = path[6:].lstrip('/')
        if rest and not rest.lower().startswith('posts/'):
            rest = f'posts/{rest}'
        return f'{media_prefix}{rest}'

    if path.lower().startswith('posts/'):
        return f'{media_prefix}{path}'

    return f'{media_prefix}posts/{path}'


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
    return _normalize_media_url(storage.url(saved_name)), media_type


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
            'media_url': _normalize_media_url(row[2]),
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
        'media_url': _normalize_media_url(row[2]),
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


@login_required
def toggle_like_view(request, post_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    user_id = request.session.get('user_id')

    try:
        if request.content_type == 'application/json':
            payload = json.loads(request.body.decode('utf-8'))
            like = payload.get('like') in (True, 'true', 1, '1')
        else:
            like = request.POST.get('like') in ('true', '1', 'on')

        procedure = 'sp_like_post' if like else 'sp_unlike_post'
        result = call_procedure(procedure, [user_id, post_id])

        if not result:
            return JsonResponse({'error': 'No result from database'}, status=500)

        row = result[0]
        return JsonResponse({
            'like_count': row[0],
            'is_liked': bool(row[1]),
        })
    except DatabaseError as error:
        return JsonResponse({'error': _database_error_message(error)}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)