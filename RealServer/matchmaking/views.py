from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from django.utils import timezone
from api.auth import custom_authenticate
from api.models import User, SexualPreference, Gender
from matchmaking.yelp import getPlacesFromYelp, TOP_RATED
from matchmaking import models
from RealServer import facebook
from messaging.models import Message
import datetime
import json
import requests
from random import randint, randrange, shuffle
from geopy.distance import great_circle

# Create your views here.
def filterBySexualPreference(user, potential_matches):
    # Filter to correct Gender based on sexual preference
    if user.interested_in != SexualPreference.BISEXUAL.value:
        potential_matches = potential_matches.filter(gender=user.interested_in)

    # Filter for potential_matches sexual preference
    potential_matches = potential_matches.filter(Q(interested_in=user.gender) |
                                                 Q(interested_in=SexualPreference.BISEXUAL.value))
    potential_matches = potential_matches.exclude(pk=user.pk)
    return potential_matches

def filterPassedMatches(user, potential_matches):
    # Exclude users who have already been passed by this user
    passed_user_pks = user.passed_matches.all().values_list('pk', flat=True)
    potential_matches = potential_matches.exclude(pk__in=passed_user_pks)
    return potential_matches

def filterByAge(user, potential_matches):
    return potential_matches.exclude(age__lte=user.min_age_preference).exclude(age__gte=user.max_age_preference)

def filterTimeAvailableUsers(user, day, potential_matches):
    # Filter to match only users who are available at same time as this user.
    # Structure query so that there is at least a one-hour meeting period for potential matches
    if day == 'sun' and user.sunday_start_time and (not user.sun_date or (user.sun_date.expires_at < timezone.now())):
        return potential_matches.filter(Q(sunday_end_time__gte=
                                                 (datetime.datetime.combine(datetime.date.today(), user.sunday_start_time) + datetime.timedelta(
                                                     hours=1)).time()) &
                                               Q(sunday_start_time__lte=
                                                 (datetime.datetime.combine(datetime.date.today(), user.sunday_end_time) - datetime.timedelta(
                                                     hours=1)).time()))\
            .filter(Q(sun_date=None) | Q(sun_date__expires_at__lt=timezone.now()))
    elif day == 'mon' and user.monday_start_time and (not user.mon_date or (user.mon_date.expires_at < timezone.now())):
        return potential_matches.filter(Q(monday_end_time__gte=
                                                 (datetime.datetime.combine(datetime.date.today(), user.monday_start_time) + datetime.timedelta(
                                                     hours=1)).time()) &
                                               Q(monday_start_time__lte=
                                                 (datetime.datetime.combine(datetime.date.today(), user.monday_end_time) - datetime.timedelta(
                                                     hours=1)).time()))\
            .filter(Q(mon_date=None) | Q(mon_date__expires_at__lt=timezone.now()))
    elif day == 'tue' and user.tuesday_start_time and (not user.tue_date or (user.tue_date.expires_at < timezone.now())):
        return potential_matches.filter(Q(tuesday_end_time__gte=
                                                 (datetime.datetime.combine(datetime.date.today(), user.tuesday_start_time) + datetime.timedelta(
                                                     hours=1)).time()) &
                                               Q(tuesday_start_time__lte=
                                                 (datetime.datetime.combine(datetime.date.today(), user.tuesday_end_time) - datetime.timedelta(
                                                     hours=1)).time()))\
            .filter(Q(tue_date=None) | Q(tue_date__expires_at__lt=timezone.now()))
    elif day == 'wed' and user.wednesday_start_time and (not user.wed_date or (user.wed_date.expires_at < timezone.now())):
        return potential_matches.filter(Q(wednesday_end_time__gte=
                                                 (datetime.datetime.combine(datetime.date.today(), user.wednesday_start_time) + datetime.timedelta(
                                                     hours=1)).time()) &
                                               Q(wednesday_start_time__lte=
                                                 (datetime.datetime.combine(datetime.date.today(), user.wednesday_end_time) - datetime.timedelta(
                                                     hours=1)).time()))\
            .filter(Q(wed_date=None) | Q(wed_date__expires_at__lt=timezone.now()))
    elif day == 'thur' and user.thursday_start_time and (not user.thur_date or (user.thur_date.expires_at < timezone.now())):
        return potential_matches.filter(Q(thursday_end_time__gte=
                                                 (datetime.datetime.combine(datetime.date.today(), user.thursday_start_time) + datetime.timedelta(
                                                     hours=1)).time()) &
                                               Q(thursday_start_time__lte=
                                                 (datetime.datetime.combine(datetime.date.today(), user.thursday_end_time) - datetime.timedelta(
                                                     hours=1)).time()))\
            .filter(Q(thur_date=None) | Q(thur_date__expires_at__lt=timezone.now()))
    elif day == 'fri' and user.friday_start_time and (not user.fri_date or (user.fri_date.expires_at < timezone.now())):
        return potential_matches.filter(Q(friday_end_time__gte=
                                                 (datetime.datetime.combine(datetime.date.today(), user.friday_start_time) + datetime.timedelta(
                                                     hours=1)).time()) &
                                               Q(friday_start_time__lte=
                                                 (datetime.datetime.combine(datetime.date.today(), user.friday_end_time) - datetime.timedelta(
                                                     hours=1)).time()))\
            .filter(Q(fri_date=None) | Q(fri_date__expires_at__lt=timezone.now()))
    elif day == 'sat' and user.saturday_start_time and (not user.sat_date or (user.sat_date.expires_at < timezone.now())):
        return potential_matches.filter(Q(saturday_end_time__gte=
                                                 (datetime.datetime.combine(datetime.date.today(), user.saturday_start_time) + datetime.timedelta(
                                                     hours=1)).time()) &
                                               Q(saturday_start_time__lte=
                                                 (datetime.datetime.combine(datetime.date.today(), user.saturday_end_time) - datetime.timedelta(
                                                     hours=1)).time()))\
            .filter(Q(sat_date=None) | Q(sat_date__expires_at__lt=timezone.now()))
    return None

def generateRandomTimeForDate(user, match, day):

    # Find correct values for day
    if day == 'sun':
        user_start_time = user.sunday_start_time
        user_end_time = user.sunday_end_time
        match_start_time = match.sunday_start_time
        match_end_time = match.sunday_end_time
    elif day == 'mon':
        user_start_time = user.monday_start_time
        user_end_time = user.monday_end_time
        match_start_time = match.monday_start_time
        match_end_time = match.monday_end_time
    elif day == 'tue':
        user_start_time = user.tuesday_start_time
        user_end_time = user.tuesday_end_time
        match_start_time = match.tuesday_start_time
        match_end_time = match.tuesday_end_time
    elif day == 'wed':
        user_start_time = user.wednesday_start_time
        user_end_time = user.wednesday_end_time
        match_start_time = match.wednesday_start_time
        match_end_time = match.wednesday_end_time
    elif day == 'thur':
        user_start_time = user.thursday_start_time
        user_end_time = user.thursday_end_time
        match_start_time = match.thursday_start_time
        match_end_time = match.thursday_end_time
    elif day == 'fri':
        user_start_time = user.friday_start_time
        user_end_time = user.friday_end_time
        match_start_time = match.friday_start_time
        match_end_time = match.friday_end_time
    elif day == 'sat':
        user_start_time = user.saturday_start_time
        user_end_time = user.saturday_end_time
        match_start_time = match.saturday_start_time
        match_end_time = match.saturday_end_time

    # Find proper values to use for time interval
    if user_start_time < match_start_time:
        date_start_time = match_start_time
    else:
        date_start_time = user_start_time
    if user_end_time > match_end_time:
        date_end_time = match_end_time
    else:
        date_end_time = user_end_time

    # Randomly choose within the time interval with intervals of 1800 seconds (30 minutes)
    date_earliest_start_td = datetime.datetime.combine(datetime.date.min, date_start_time) - datetime.datetime.min
    date_latest_start_td = datetime.datetime.combine(datetime.date.min, date_end_time) - datetime.datetime.min \
                           - datetime.timedelta(hours=1)

    # If times are not equal, generate a random start time in interval. If they are equal, use that as start time.
    if date_earliest_start_td != date_latest_start_td:
        date_rand_start_td = datetime.timedelta(seconds=randrange(date_earliest_start_td.seconds,
                                                                  date_latest_start_td.seconds, 1800))
    else:
        date_rand_start_td = date_earliest_start_td
    date_start_time = (datetime.datetime.min + date_rand_start_td).time()
    return date_start_time


def makeDate(user, day, potential_matches):
    interests = []
    if user.likes_drinks:
        interests.append('drinks')
    if user.likes_food:
        interests.append('food')
    if user.likes_coffee:
        interests.append('coffee')
    if user.likes_nature:
        interests.append('nature')
    if user.likes_culture:
        interests.append('culture')
    if user.likes_active:
        interests.append('active')
    # Choose a random category. If no match is found in category, try another category until all options exhausted
    match = None
    first_category_index = randint(0, len(interests)-1)
    category_index = (first_category_index + 1) % len(interests)
    while True:
        category = interests[category_index]
        # Filter potential matches based on category
        if category == 'drinks':
            category_filtered = potential_matches.filter(likes_drinks=True)
        elif category == 'food':
            category_filtered = potential_matches.filter(likes_food=True)
        elif category == 'coffee':
            category_filtered = potential_matches.filter(likes_coffee=True)
        elif category == 'nature':
            category_filtered = potential_matches.filter(likes_nature=True)
        elif category == 'culture':
            category_filtered = potential_matches.filter(likes_culture=True)
        elif category == 'active':
            category_filtered = potential_matches.filter(likes_active=True)
        category_filtered = list(category_filtered)
        shuffle(category_filtered) # Potential matches are randomly sorted
        # Choose a place randomly from TOP_RATED places. If no match found, iterate through places until all options exhausted
        if category_filtered:
            places = getPlacesFromYelp(user, category)
            places = places[0:TOP_RATED]
            first_place_index = randint(0, len(places)-1)
            place_index = (first_place_index + 1) % len(places)
            while True:
                place = places[place_index]
                # Calculate distance to place for each potential match
                for potential_match in category_filtered:
                    match_coordinates = (potential_match.latitude, potential_match.longitude)
                    place_coordinates = (place['coordinates']['latitude'], place['coordinates']['longitude'])
                    if great_circle(match_coordinates, place_coordinates).miles < potential_match.search_radius:
                        match = potential_match
                        # Only match if user is not already matched with match this week
                        if (user.sun_date and (user.sun_date.user1 == match or user.sun_date.user2 == match)) or\
                            (user.mon_date and (user.mon_date.user1 == match or user.mon_date.user2 == match)) or\
                            (user.tue_date and (user.tue_date.user1 == match or user.tue_date.user2 == match)) or\
                            (user.wed_date and (user.wed_date.user1 == match or user.wed_date.user2 == match)) or\
                            (user.thur_date and (user.thur_date.user1 == match or user.thur_date.user2 == match)) or\
                            (user.fri_date and (user.fri_date.user1 == match or user.fri_date.user2 == match)) or\
                            (user.sat_date and (user.sat_date.user1 == match or user.sat_date.user2 == match)):
                            match = None
                            continue
                        break

                if match or place_index == first_place_index:
                    break
                place_index = (place_index + 1) % len(places)

        if match or category_index == first_category_index:
            break
        category_index = (category_index + 1) % len(interests)

    if not match:
        return None
    else:
        time = generateRandomTimeForDate(user, match, day)
        date = models.Date(user1=user, user2=match, day=day, start_time=time, expires_at=(timezone.now() + datetime.timedelta(hours=24)),
                    place_id=place['id'], place_name=place['name'], category=interests[category_index])
        date.original_expires_at = date.expires_at
        date.save()
        setattr(user, day+'_date', date)
        setattr(match, day+'_date', date)
        user.save()
        match.save()
        return date

def convertDateToJson(user,date):

    # Add fields that don't have ambiguity around user
    json = {
        'date_id': date.pk,
        'respond_by': date.expires_at.isoformat(),
        'time':
            {
                'day': date.day,
                'start_time': date.start_time.isoformat()
            },
        'place':
            {
                'place_id': date.place_id,
                'name': date.place_name,
            }
    }

    try:
        last_sent_message = date.message_set.order_by('-index')[0]
        json['last_sent_message'] = last_sent_message.content
        json['message_read'] = last_sent_message.read
    except IndexError:
        pass

    # Determine to which user the Date fields are relative
    if date.user1 == user:
        potential_match = date.user2
        if date.user2_likes == models.DateStatus.LIKES.value:
            json['potential_match_likes'] = True
        else:
            json['potential_match_likes'] = False
        json['primary_user_likes'] = date.user1_likes
    else:
        potential_match = date.user1
        if date.user1_likes == models.DateStatus.LIKES.value:
            json['potential_match_likes'] = True
        else:
            json['potential_match_likes'] = False
        json['primary_user_likes'] = date.user2_likes

    json['match'] = {
        'user_id': potential_match.pk,
        'name': potential_match.name,
        'age': potential_match.age,
        'occupation': potential_match.occupation,
        'education': potential_match.education,
        'about': potential_match.about,
        'main_picture': potential_match.picture1,
        'additional_pictures': [
            potential_match.picture2, potential_match.picture3, potential_match.picture4, potential_match.picture5,
            potential_match.picture6
        ]
    }

    # Get Mutual Friends
    mutual_friends_json = facebook.getMutualFriends(user, potential_match)
    if mutual_friends_json:
        mutual_friends_json = mutual_friends_json['data']
        mutual_friends = []
        for friend in mutual_friends_json:
            mutual_friends.append({
                'friend': {
                    'name': friend['name'],
                    'picture': friend['picture']['data']['url']
                }
            })
        json['match']['mutual_friends'] = mutual_friends

    return json



#@csrf_exempt
#@custom_authenticate
def date(request, user, day):
    # If date already exists, return date
    if getattr(user, day + '_date') and getattr(user, day + '_date').expires_at >= timezone.now():
        return JsonResponse(json.dumps(convertDateToJson(user, getattr(user, day + '_date'))), safe=False)
    else: # Query for a match and create date from those matches
        potential_matches = filterBySexualPreference(user, User.objects.exclude(pk=user.pk))
        potential_matches = filterByAge(user, potential_matches)
        potential_matches = filterPassedMatches(user, potential_matches)
        potential_matches = filterTimeAvailableUsers(user, day, potential_matches)
        makeDate(user, day, potential_matches)
        if getattr(user, day + '_date'):
            return JsonResponse(json.dumps(convertDateToJson(user, getattr(user, day + '_date'))), safe=False)
        else:
            return JsonResponse(json.dumps(None), safe=False)