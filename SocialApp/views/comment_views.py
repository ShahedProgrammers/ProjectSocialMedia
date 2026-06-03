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

@login_required
def post_comments_view(request, post_id):
    if request.method == 'GET':
        try:
            rows = call_procedure('sp_get_post_comments', [post_id]) or []
            comments = [{
                'comment_id': row[0],
                'username': row[1],
                'content': row[2],
                'created_at': row[3].strftime('%Y/%m/%d %H:%M') if row[3] else '',
            } for row in rows]
            return JsonResponse({'comments': comments})
        except DatabaseError as error:
            return JsonResponse({'error': _database_error_message(error)}, status=400)

    if request.method == 'POST':
        user_id = request.session.get('user_id')

        try:
            if request.content_type == 'application/json':
                payload = json.loads(request.body.decode('utf-8'))
                content = payload.get('content', '').strip()
            else:
                content = request.POST.get('content', '').strip()

            result = call_procedure('sp_add_comment', [user_id, post_id, content])
            comment_id = result[0][0] if result else None

            return JsonResponse({
                'comment': {
                    'comment_id': comment_id,
                    'username': request.session.get('username', ''),
                    'content': content,
                    'created_at': datetime.now().strftime('%Y/%m/%d %H:%M'),
                }
            })
        except DatabaseError as error:
            return JsonResponse({'error': _database_error_message(error)}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

    return JsonResponse({'error': 'Method not allowed'}, status=405)