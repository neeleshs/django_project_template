'''
Created on 01-Nov-2010

@author: neelesh
'''
from settings import MEDIA_URL, UI_DATE_FORMAT, APP_NAME, APP_DESC

def media_url(request):
    return {'MEDIA_URL':(MEDIA_URL if MEDIA_URL else '/public')}        

def date_format(request):
    return {'DATE_FORMAT':UI_DATE_FORMAT}

def today(request):
    from datetime import date
    return {'today':date.today()}

def theme(request):
    return {'THEME':'smoothness'}

def template(request):
    base_template ='template.html'
    return {'BASE_TEMPLATE':base_template}

def app_details(request):
    return {'APP_NAME':APP_NAME,'APP_DESC':APP_DESC}

