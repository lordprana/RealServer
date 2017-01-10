from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from api.auth import custom_authenticate
from api.models import User, SexualPreference, Gender
from matchmaking.yelp import getPlacesFromYelp, TOP_RATED
from matchmaking import models
import datetime
from random import randint
from geopy.distance import great_circle

# Create your views here.

def filterBySexualPreference(user):
    # Filter to correct Gender based on sexual preference
    if user.interested_in != SexualPreference.BISEXUAL.value:
        potential_matches = User.objects.filter(gender=user.interested_in)
    else:
        potential_matches = User.objects.all()
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

def filterTimeAvailableUsers(user, potential_matches):
    #TODO: Implement threading to speed this up
    # Filter to match only users who are available at same time as this user
    days = {}
    if user.sunday_start_time and (not user.sun_date or (user.sun_date.expires_at < datetime.datetime.now())):
        days['sun'] = potential_matches.filter(Q(sunday_end_time__gte=
                                                 (datetime.datetime.combine(datetime.date.today(), user.sunday_start_time) + datetime.timedelta(
                                                     hours=1)).time()) &
                                               Q(sunday_start_time__lte=
                                                 (datetime.datetime.combine(datetime.date.today(), user.sunday_end_time) - datetime.timedelta(
                                                     hours=1)).time()))\
            .filter(Q(sun_date=None) | Q(sun_date__expires_at__lt=datetime.datetime.now()))
    if user.monday_start_time and (not user.mon_date or (user.mon_date.expires_at < datetime.datetime.now())):
        days['mon'] = potential_matches.filter(Q(monday_end_time__gte=
                                                 (datetime.datetime.combine(datetime.date.today(), user.monday_start_time) + datetime.timedelta(
                                                     hours=1)).time()) &
                                               Q(monday_start_time__lte=
                                                 (datetime.datetime.combine(datetime.date.today(), user.monday_end_time) - datetime.timedelta(
                                                     hours=1)).time()))\
            .filter(Q(mon_date=None) | Q(mon_date__expires_at__lt=datetime.datetime.now()))
    if user.tuesday_start_time and (not user.tue_date or (user.tue_date.expires_at < datetime.datetime.now())):
        days['tue'] = potential_matches.filter(Q(tuesday_end_time__gte=
                                                 (datetime.datetime.combine(datetime.date.today(), user.tuesday_start_time) + datetime.timedelta(
                                                     hours=1)).time()) &
                                               Q(tuesday_start_time__lte=
                                                 (datetime.datetime.combine(datetime.date.today(), user.tuesday_end_time) - datetime.timedelta(
                                                     hours=1)).time())).\
            filter(Q(tue_date=None) | Q(tue_date__expires_at__lt=datetime.datetime.now()))
    if user.wednesday_start_time and (not user.wed_date or (user.wed_date.expires_at < datetime.datetime.now())):
        days['wed'] = potential_matches.filter(Q(wednesday_end_time__gte=
                                                 (datetime.datetime.combine(datetime.date.today(), user.wednesday_start_time) + datetime.timedelta(
                                                     hours=1)).time()) &
                                               Q(wednesday_start_time__lte=
                                                 (datetime.datetime.combine(datetime.date.today(), user.wednesday_end_time) - datetime.timedelta(
                                                     hours=1)).time()))\
            .filter(Q(wed_date=None) | Q(wed_date__expires_at__lt=datetime.datetime.now()))
    if user.thursday_start_time and (not user.thur_date or (user.thur_date.expires_at < datetime.datetime.now())):
        days['thur'] = potential_matches.filter(Q(thursday_end_time__gte=
                                                 (datetime.datetime.combine(datetime.date.today(), user.thursday_start_time) + datetime.timedelta(
                                                     hours=1)).time()) &
                                               Q(thursday_start_time__lte=
                                                 (datetime.datetime.combine(datetime.date.today(), user.thursday_end_time) - datetime.timedelta(
                                                     hours=1)).time()))\
            .filter(Q(thur_date=None) | Q(thur_date__expires_at__lt=datetime.datetime.now()))
    if user.friday_start_time and (not user.fri_date or (user.fri_date.expires_at < datetime.datetime.now())):
        days['fri'] = potential_matches.filter(Q(friday_end_time__gte=
                                                 (datetime.datetime.combine(datetime.date.today(), user.friday_start_time) + datetime.timedelta(
                                                     hours=1)).time()) &
                                               Q(friday_start_time__lte=
                                                 (datetime.datetime.combine(datetime.date.today(), user.friday_end_time) - datetime.timedelta(
                                                     hours=1)).time()))\
            .filter(Q(fri_date=None) | Q(fri_date__expires_at__lt=datetime.datetime.now()))
    if user.saturday_start_time and (not user.sat_date or (user.sat_date.expires_at < datetime.datetime.now())):
        days['sat'] = potential_matches.filter(Q(saturday_end_time__gte=
                                                 (datetime.datetime.combine(datetime.date.today(), user.saturday_start_time) + datetime.timedelta(
                                                     hours=1)).time()) &
                                               Q(saturday_start_time__lte=
                                                 (datetime.datetime.combine(datetime.date.today(), user.saturday_end_time) - datetime.timedelta(
                                                     hours=1)).time()))\
            .filter(Q(sat_date=None) | Q(sat_date__expires_at__lt=datetime.datetime.now()))
    return days

def dayToDate(user, day, potential_matches):
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

        # Choose a place randomly from TOP_RATED places. If no match found, iterate through places until all options exhausted
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
                    break
            if match or place_index == first_place_index:
                break
            place_index = (place_index + 1) % len(places)

        if match or category_index == first_category_index:
            break
        category_index = (category_index + 1) % len(interests)

    if not match:
        return None, None
    else:
        date = models.Date(user1=user, user2=match, expires_at=(datetime.datetime.now() + datetime.timedelta(hours=24)),
                    place_id=place['id'], category=interests[category_index])
        date.save()
        setattr(user, day+'_date', date)
        setattr(match, day+'_date', date)
        user.save()
        match.save()
        print(type(user))
        print(type(match))
        return date, place




@csrf_exempt
@custom_authenticate
def dateslist(request, user):
    potential_matches = filterBySexualPreference(user)
    potential_matches = filterPassedMatches(user, potential_matches)
    days = filterTimeAvailableUsers(user, potential_matches)
    for day, potential_matches in days.viewitems():
        # Randomly choose a date category
        date, place = dayToDate(user, day, potential_matches)
        print(date)
        print(place)