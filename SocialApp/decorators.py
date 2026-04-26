from django.shortcuts import redirect

def login_required(veiw_func) :
    def wrapper(request , *args , **kwargs) :
        if 'user_id' not in request.session:
            return redirect('login')
        return veiw_func(request , *args , **kwargs)
    return wrapper