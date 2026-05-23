from django.db import connection

def execute(sql , params = None):
    with connection.cursor() as cursor :
        cursor.execute(sql , params or [])
        
def fetch_all(sql , params = None):
    with connection.cursor() as cursor :
        cursor.execute(sql , params or [])
        return cursor.fetchall()
    
    
def fetch_one(sql , params = None):
    with connection.cursor() as cursor :
        cursor.execute(sql , params or [])
        return cursor.fetchone()
    
def call_procedure(sql , params = None):
    with connection.cursor() as cursor :
        cursor.callproc(sql , params or [])
        rows = []
        while True:
            if cursor.description:
                fetched = cursor.fetchall()
                if fetched:
                    rows = fetched
            if not cursor.nextset():
                break
        return rows
