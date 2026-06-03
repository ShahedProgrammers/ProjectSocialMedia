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
def home_feed_view(request):
    user_id = request.session.get('user_id')
    username = request.session.get('username', 'کاربر')

    try:
        rows = call_procedure('sp_get_home_feed', [user_id]) or []
    except DatabaseError:
        rows = []

    posts = []
    for row in rows:
        author_pic = None
        if row[3]:
            author_pic = base64.b64encode(bytes(row[3])).decode('utf-8')

        tags_raw = row[10] or ''
        tags = [t.strip() for t in tags_raw.split(',') if t.strip()]

        posts.append({
            'post_id':          row[0],
            'author_user_id':   row[1],
            'author_username':  row[2],
            'author_pic':       author_pic,
            'caption':          row[4] or '',
            'media_url':        _normalize_media_url(row[5]),
            'media_type':       row[6],
            'created_at':       row[7].strftime('%Y/%m/%d %H:%M') if row[7] else '',
            'comments_enabled': row[8],
            'like_count':       row[9],
            'tags':             tags,
            'is_liked':         bool(row[11]),
        })

    return render(request, 'home/index.html', {
        'username':    username,
        'profile_pic': _get_profile_pic_b64(user_id),
        'posts':       posts,
    })