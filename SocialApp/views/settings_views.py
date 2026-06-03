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
