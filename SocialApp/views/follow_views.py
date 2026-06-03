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

def _database_error_message(error):
    return str(error).split("MESSAGE_TEXT =")[-1].strip() if "MESSAGE_TEXT =" in str(error) else str(error)

def _is_following(follower_id, following_id):
    result = call_procedure('sp_is_following', [follower_id, following_id])
    if result and result[0]:
        return bool(result[0][0])
    return False




def _get_followers_count(user_id):
    row = fetch_one(
        "SELECT COUNT(*) FROM FollowsApp WHERE FollowingID = %s",
        [user_id],
    )
    return row[0] if row else 0


def _follow_user(follower_id, following_id):
    try:
        call_procedure('sp_follow_user', [follower_id, following_id])
    except DatabaseError as error:
        raise ValueError(_database_error_message(error))


def _unfollow_user(follower_id, following_id):
    call_procedure('sp_unfollow_user', [follower_id, following_id])


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


def _fetch_followers(user_id, viewer_id):
    return call_procedure('sp_get_user_followers', [user_id, viewer_id]) or []

def _fetch_followings(user_id, viewer_id):
    return call_procedure('sp_get_user_followings', [user_id, viewer_id]) or []

def _parse_user_list(rows):
    users = []
    for row in rows:
        profile_pic = None
        if row[2]:
            profile_pic = base64.b64encode(bytes(row[2])).decode('utf-8')
        users.append({
            'user_id': row[0],
            'username': row[1],
            'profile_pic': profile_pic,
            'is_following': bool(row[3]),
        })
    return users


@login_required
def toggle_follow_view(request, user_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    follower_id = request.session.get('user_id')

    try:
        if request.content_type == 'application/json':
            payload = json.loads(request.body.decode('utf-8'))
            follow = payload.get('follow') in (True, 'true', 1, '1')
        else:
            follow = request.POST.get('follow') in ('true', '1', 'on')

        if follow:
            _follow_user(follower_id, user_id)
        else:
            _unfollow_user(follower_id, user_id)

        return JsonResponse({
            'followers_count': _get_followers_count(user_id),
            'is_following': _is_following(follower_id, user_id),
        })
    except ValueError as error:
        return JsonResponse({'error': str(error)}, status=400)
    except DatabaseError as error:
        return JsonResponse({'error': _database_error_message(error)}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)




@login_required
def user_followers_view(request, user_id):
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    viewer_id = request.session.get('user_id')

    try:
        rows = _fetch_followers(user_id, viewer_id) or []
        return JsonResponse({'users': _parse_user_list(rows)})
    except DatabaseError as error:
        return JsonResponse({'error': _database_error_message(error)}, status=400)


@login_required
def user_followings_view(request, user_id):
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    viewer_id = request.session.get('user_id')

    try:
        rows = _fetch_followings(user_id, viewer_id) or []
        return JsonResponse({'users': _parse_user_list(rows)})
    except DatabaseError as error:
        return JsonResponse({'error': _database_error_message(error)}, status=400)