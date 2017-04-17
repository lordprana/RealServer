from datetime import timedelta, time, datetime
import requests
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from RealServer.settings import YELP_APP_ID, YELP_APP_SECRET
from matchmaking.models import YelpAccessToken, YelpBusinessDetails

CATEGORY_MAPPING = {
    'drinks': 'bars',
    'food': 'restaurants',
    'coffee': 'coffee',
    'museums': 'museums',
    'parks': 'parks',
    'fun': 'active'
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

def refreshPlaceDetailsOnNetwork(id):
    access_token = YelpAccessToken.objects.filter(expires_at__gt=timezone.now())
    if access_token.count() == 0:
        token = refreshAccessToken()
    else:
        token = access_token[0].access_token
    request_url = 'https://api.yelp.com/v3/businesses/' + id
    headers = {'Authorization': 'Bearer ' + token}
    response = requests.get(request_url, headers=headers)
    if response.status_code != 200:
        response.raise_for_status()
    response_json = response.json()
    hours = {}
    days = ['mon', 'tue', 'wed', 'thur', 'fri', 'sat', 'sun']
    place_details = YelpBusinessDetails(place_id=id, place_name=response_json['name'])
    # If there is no hours parameter, it means the location is always open, like a park, so we set the start and end
    # times to be available all day. If there is an hours parameter, parse appropriately.
    if not response_json.get('hours', None):
        for i in range(0, 7):
            setattr(place_details, days[i] + '_start_time', time(hour=6))
            setattr(place_details, days[i] + '_end_time', time(hour=23, minute=59, second=59))
            # hours[days[i]] = {}
            # hours[days[i]]['start'] = time(hour=6)
            # hours[days[i]]['end'] = time(hour=23, minute=59, second=59)
    else:
        # There is a known issue in this parsing code. Sometimes Yelp returns more than one time segment. An example
        # of this is with the biz_id 'royal-thai-dallas'. It is open in the afternoon, closes, and then opens again
        # for the evening. The code below will take the latest time segment returned.
        yelp_hours = response_json['hours'][0]['open']
        for i in range(0, 7):
            # hours[days[i]] = {}
            for j in range(0, len(yelp_hours)):
                if yelp_hours[j]['day'] == i:
                    # hours[days[i]]['start'] = datetime.strptime(yelp_hours[j]['start'], '%H%M').time()
                    setattr(place_details, days[i] + '_start_time', datetime.strptime(yelp_hours[j]['start'], '%H%M').time())
                    # is_overnight means the hours are overnight. For matching purposes, we set the endtime to the last
                    # second of the current day.
                    if yelp_hours[j]['is_overnight']:
                        # hours[days[i]]['end'] = time(hour=23, minute=59, second=59)
                        setattr(place_details, days[i] + '_end_time', time(hour=23, minute=59, second=59))
                    else:
                        # hours[days[i]]['end'] = datetime.strptime(yelp_hours[j]['end'], '%H%M').time()
                        setattr(place_details, days[i] + '_end_time', datetime.strptime(yelp_hours[j]['end'], '%H%M').time())
                        # Midnight is late on current day, not early on current day, so this condition fixes comparing times when trying
                        # to generate a random time for the date
                        # if hours[days[i]]['end'] == time(hour=0, minute=0, second=0):
                        # hours[days[i]]['end'] = time(hour=23, minute=59, second=59)
                        if getattr(place_details, days[i] + '_end_time') == time(hour=0, minute=0, second=0):
                            setattr(place_details, days[i] + '_end_time', time(hour=23, minute=59, second=59))
    return place_details

def getPlaceDetailsFromYelp(id):
    try:
        place_details = YelpBusinessDetails.objects.get(place_id=id)
        return place_details
    except ObjectDoesNotExist:
        pass # Code below handles when there is no place matching place id in database

    place_details = refreshPlaceDetailsOnNetwork(id)
    place_details.save()
    return place_details