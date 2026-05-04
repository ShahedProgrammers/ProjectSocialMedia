import base64
from .Function_sql import fetch_one

def user_profile_pic(request):
    profile_pic = None
    if request.session.get('user_id'):
        try:
            result = fetch_one("SELECT ProfilePic FROM Users WHERE UserID=%s", [request.session['user_id']])
            if result and result[0]:
                profile_pic = base64.b64encode(result[0]).decode('utf-8')
        except Exception as e:
            print(f"Error loading profile pic: {e}")
    return {'profile_pic': profile_pic}
