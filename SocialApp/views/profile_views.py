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


def _parse_my_posts(user_id, viewer_user_id=None):
    rows = call_procedure('sp_get_my_posts', [user_id]) or []

    liked_post_ids = set()
    if viewer_user_id and rows:
        post_ids = [row[0] for row in rows]
        placeholders = ','.join(['%s'] * len(post_ids))
        liked_rows = fetch_all(
            f"SELECT PostID FROM Likes WHERE UserID=%s AND PostID IN ({placeholders})",
            [viewer_user_id, *post_ids],
        )
        liked_post_ids = {row[0] for row in liked_rows}

    posts = []
    for row in rows:
        posts.append({
            'post_id': row[0],
            'caption': row[1] or '',
            'media_url': _normalize_media_url(row[2]),
            'media_type': row[3],
            'comments_enabled': row[4],
            'scheduled_time': row[5],
            'created_at': row[6],
            'like_count': row[7],
            'is_liked': row[0] in liked_post_ids,
        })
    return posts



def _is_following(follower_id, following_id):
    result = call_procedure('sp_is_following', [follower_id, following_id])
    if result and result[0]:
        return bool(result[0][0])
    return False



@login_required
def profile_view(request, user_id=None):

    session_user_id = request.session.get('user_id')
    profile_user_id = user_id or session_user_id
    is_own_profile = profile_user_id == session_user_id

    try:
        result = call_procedure('sp_get_user_summary', [profile_user_id])

        if not result:
            return redirect('explore' if user_id else 'home')

        user = result[0]
        posts = _parse_my_posts(profile_user_id, session_user_id)

        profile = {
            'user_id': user[0],
            'username': user[1],
            'bio': user[2] if user[2] else '',
        }

        profile_pic = None
        if user[3]:
            profile_pic = base64.b64encode(bytes(user[3])).decode('utf-8')

        is_following = False
        if not is_own_profile:
            is_following = _is_following(session_user_id, profile_user_id)

        return render(request, 'profile/profile.html', {
            'profile': profile,
            'profile_pic': profile_pic,
            'posts': posts,
            'posts_count': len(posts),
            'followers_count': user[4],
            'followings_count': user[5],
            'is_own_profile': is_own_profile,
            'is_following': is_following,
        })

    except DatabaseError:
        return redirect('explore' if user_id else 'home')



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