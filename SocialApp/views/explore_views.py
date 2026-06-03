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

def _get_following_user_ids(viewer_id, user_ids):
    if not viewer_id or not user_ids:
        return set()

    unique_ids = list(dict.fromkeys(user_ids))
    placeholders = ','.join(['%s'] * len(unique_ids))
    rows = fetch_all(
        f"""
        SELECT FollowingID
          FROM FollowsApp
         WHERE FollowerID = %s
           AND FollowingID IN ({placeholders})
        """,
        [viewer_id, *unique_ids],
    )
    return {row[0] for row in rows}

def _parse_explore_feed(user_id):
    rows = call_procedure('sp_get_explore_feed', [user_id]) or []
    posts = []
    author_ids = []

    for row in rows:
        author_ids.append(row[1])

        author_pic = None
        if row[3]:
            author_pic = base64.b64encode(bytes(row[3])).decode('utf-8')

        tags_raw = row[10] or ''
        tags = [tag.strip() for tag in tags_raw.split(',') if tag.strip()] if tags_raw else []

        posts.append({
            'post_id': row[0],
            'author_user_id': row[1],
            'author_username': row[2],
            'author_profile_pic': author_pic,
            'caption': row[4] or '',
            'media_url': _normalize_media_url(row[5]),
            'media_type': row[6],
            'created_at': row[7].strftime('%Y/%m/%d %H:%M') if row[7] else '',
            'comments_enabled': row[8],
            'like_count': row[9],
            'tags': tags,
            'is_liked': bool(row[11]),
            'is_following': False,
        })

    if user_id and posts:
        following_ids = _get_following_user_ids(user_id, author_ids)
        for post in posts:
            post['is_following'] = post['author_user_id'] in following_ids

    return posts

def _get_profile_pic_b64(user_id):
    try:
        result = fetch_one(
            "SELECT ProfilePic FROM Users WHERE UserID=%s",
            [user_id]
        )
        if result and result[0]:
            return base64.b64encode(bytes(result[0])).decode('utf-8')
    except Exception:
        pass
    return None


@login_required
def explore_view(request):
    user_id = request.session.get('user_id')
    username = request.session.get('username', 'کاربر')

    try:
        posts = _parse_explore_feed(user_id)
    except DatabaseError:
        posts = []

    return render(request, 'explore/explore.html', {
        'username': username,
        'profile_pic': _get_profile_pic_b64(user_id),
        'current_user_id': user_id,
        'posts': posts,
    })

