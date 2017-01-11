import requests
from RealServer.settings import YELP_APP_ID, YELP_APP_SECRET
from matchmaking.models import YelpAccessToken
from datetime import datetime, timedelta
from django.utils import timezone

CATEGORY_MAPPING = {
    'drinks': 'bars',
    'food': 'restaurants',
    'coffee': 'coffee',
    'culture': 'museums',
    'nature': 'parks',
    'active': 'active'
}

TOP_RATED = 10

def refreshAccessToken():
    request_url = 'https://api.yelp.com/oauth2/token'
    data = {
        'grant_type': 'client_credentials',
        'client_id': YELP_APP_ID,
        'client_secret': YELP_APP_SECRET
    }
    response = requests.post(request_url, data=data)
    token = response.json()['access_token']
    expires_at = timedelta(seconds=response.json()['expires_in']) + timezone.now()
    YelpAccessToken.objects.create(access_token=token, expires_at=expires_at)
    return token

def getPlacesFromYelp(user, category):
    access_token = YelpAccessToken.objects.filter(expires_at__gt=timezone.now())
    if access_token.count() == 0:
        token = refreshAccessToken()
    else:
        token = access_token[0].access_token
    radius = int(user.search_radius * 1609.34) #convert miles to meters
    price = ''
    for i in range(1,user.max_price+1):
        price = price + str(i) + ','

    request_url = 'https://api.yelp.com/v3/businesses/search?latitude='+str(user.latitude)+\
                  '&longitude='+str(user.longitude)+'&radius='+str(radius)+\
                  '&categories='+CATEGORY_MAPPING[category]
    headers = {'Authorization': 'Bearer ' + token }
    response = requests.get(request_url, headers=headers)
    if response.status_code != 200:
        response.raise_for_status()
    businesses_list = response.json()['businesses']
    return_list = []
    for item in businesses_list:
        for i in range(0, user.max_price+1):
            price = '$'*i
            if item.get('price', '') == price:
                return_list.append(item)
    return return_list
