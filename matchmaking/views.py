from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, F
from django.db import transaction
from django.utils import timezone
from api.auth import custom_authenticate
from api.models import User, SexualPreference, Gender, Status
from matchmaking.yelp import getPlacesFromYelp, TOP_RATED, getPlaceHoursFromYelp
from matchmaking import models
from RealServer import facebook
from RealServer.tools import convertLocalTimeToUTC
from messaging.models import Message
import datetime
import json
import requests
from pytz import timezone as pytz_timezone
import pytz
from random import randint, randrange, shuffle
from geopy.distance import great_circle

def filterByUserStatus(potential_matches):
    return potential_matches.exclude(status=Status.INACTIVE.value)

def filterFakeUsers(potential_matches):
    return potential_matches.exclude(is_fake_user=True)

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
    if getattr(user, day + '_start_time') and (not getattr(user, day + '_date') or getattr(user, day + '_date').expires_at < timezone.now()):
        # Filter to match only users who are available at same time as this user.
        # Structure query so that there is at least a one-hour meeting period for potential matches
        q1_dict = { day + '_end_time__gte': (datetime.datetime.combine(datetime.date.today(), getattr(user, day + '_start_time')) + datetime.timedelta(
                                                     hours=1)).time() }
        q2_dict = { day + '_start_time__lte': (datetime.datetime.combine(datetime.date.today(), getattr(user, day + '_end_time')) - datetime.timedelta(
                                                     hours=1)).time() }
        # Filter to match only users who have not already been scheduled for a date on this day
        q3_dict = { day + '_date': None }
        q4_dict = { day + '_date__expires_at__lt': timezone.now()}
        return potential_matches.filter(Q(**q1_dict) & Q(**q2_dict)).filter(Q(**q3_dict) | Q(**q4_dict))
    else:
        return User.objects.none()

def filterByLatitudeLongitude(user, potential_matches):
    filter_radius = 1
    return potential_matches.filter(latitude__gte=(user.latitude - filter_radius)).filter(latitude__lte=(user.latitude + filter_radius))\
                        .filter(longitude__gte=(user.longitude - filter_radius)).filter(longitude__lte=(user.longitude + filter_radius))

def generateDateOfDateFromDay(day):
    days = ['mon', 'tue', 'wed', 'thur', 'fri', 'sat', 'sun']
    date_of_date = timezone.now().date()
    current_day = date_of_date.weekday()
    while days[current_day] != day:
        date_of_date = date_of_date + datetime.timedelta(days=1)
        current_day = date_of_date.weekday()
    return date_of_date

def generateRandomTimeForDate(user, match, day, category, location_times):
    if not location_times:
        return None

    # Find correct values for day
    user_start_time = getattr(user, day + '_start_time')
    user_end_time = getattr(user, day + '_end_time')
    match_start_time = getattr(match, day + '_start_time')
    match_end_time = getattr(match, day + '_end_time')

    # Find proper values to use for time interval
    if user_start_time < match_start_time:
        date_start_time = match_start_time
    else:
        date_start_time = user_start_time
    if date_start_time < models.Date.appropriate_times[category]['start']:
        date_start_time = models.Date.appropriate_times[category]['start']
    if date_start_time < location_times['start']:
        date_start_time = location_times['start']

    if user_end_time > match_end_time:
        date_end_time = match_end_time
    else:
        date_end_time = user_end_time
    if date_end_time > models.Date.appropriate_times[category]['end']:
        date_end_time = models.Date.appropriate_times[category]['end']
    if date_end_time > location_times['end']:
        date_end_time = location_times['end']

    # Randomly choose within the time interval with intervals of 1800 seconds (30 minutes)
    date_earliest_start_td = datetime.datetime.combine(datetime.date.min, date_start_time) - datetime.datetime.min
    date_latest_start_td = datetime.datetime.combine(datetime.date.min, date_end_time) - datetime.datetime.min \
                           - datetime.timedelta(hours=1)

    if date_latest_start_td < date_earliest_start_td:
        return None

    # If times are not equal, generate a random start time in interval. If they are equal, use that as start time.
    if date_earliest_start_td != date_latest_start_td:
        date_rand_start_td = datetime.timedelta(seconds=randrange(date_earliest_start_td.seconds,
                                                                  date_latest_start_td.seconds, 1800))
    else:
        date_rand_start_td = date_earliest_start_td
    date_start_time = (datetime.datetime.min + date_rand_start_td).time()
    return date_start_time

def filterByAppropriateCategoryTimes(user, potential_matches, day, category):
    # First, check if user's times fall within appropriate window for the category times. If so, filter for potential
    # matches that fall within appropriate category times
    if (getattr(user, day + '_end_time') >= (datetime.datetime.combine(datetime.date.today(),
                                                                       models.Date.appropriate_times[category]['start'])
                                                 + datetime.timedelta(hours=1)).time()) and\
        (getattr(user, day + '_start_time') <= (datetime.datetime.combine(datetime.date.today(),
                                                                        models.Date.appropriate_times[category]['end'])
                                                   - datetime.timedelta(hours=1)).time()):
        q1_dict = { day + '_end_time__gte': (
        datetime.datetime.combine(datetime.date.today(), models.Date.appropriate_times[category]['start'])
        + datetime.timedelta(hours=1)).time() }
        q2_dict = {day + '_start_time__lte': (
        datetime.datetime.combine(datetime.date.today(), models.Date.appropriate_times[category]['end'])
        - datetime.timedelta(hours=1)).time()}
        return potential_matches.filter(Q(**q1_dict) & Q(**q2_dict))
    else:
        return User.objects.none()

@transaction.atomic
def makeDate(user, day, potential_matches):
    # Use select_for_update to lock user's row
    user = User.objects.select_for_update().get(pk=user.pk)
    interests = []
    if user.likes_drinks:
        interests.append('drinks')
    if user.likes_food:
        interests.append('food')
    if user.likes_coffee:
        interests.append('coffee')
    if user.likes_parks:
        interests.append('parks')
    if user.likes_museums:
        interests.append('museums')
    if user.likes_fun:
        interests.append('fun')
    # Choose a random category. If no match is found in category, try another category until all options exhausted
    match = None
    first_category_index = randint(0, len(interests)-1)
    category_index = (first_category_index + 1) % len(interests)
    while True:
        category = interests[category_index]
        # Filter potential matches based on category
        filter_dict = {'likes_' + category: True}
        category_filtered = potential_matches.filter(**filter_dict)

        category_filtered = filterByAppropriateCategoryTimes(user, category_filtered, day, category)
        # Choose a place randomly from TOP_RATED places. If no match found, iterate through places until all options exhausted
        if category_filtered:
            places = getPlacesFromYelp(user, category)
            if not places:
                # Check for end loop condition, if not end loop, increment loop
                if category_index == first_category_index:
                    break
                category_index = (category_index + 1) % len(interests)
                continue
            if len(places) >= TOP_RATED:
                places = places[0:TOP_RATED]
            first_place_index = randint(0, len(places)-1)
            place_index = (first_place_index + 1) % len(places)
            while True:
                place = places[place_index]
                # Filter for users who have a max_price setting greater than price of place
                price_filtered = category_filtered.filter(max_price__gte=place.get('price', '').count('$'))

                # If user is a new user (less than a week old) show him more attractive potential matches
                if timezone.now() > user.created + datetime.timedelta(days=7):
                    potential_matches = list(price_filtered)
                    shuffle(potential_matches) # Potential matches are randomly sorted
                else:
                    num_times_suggested_threshold = 10
                    like_score_threshold = .6
                    attractive_matches = price_filtered.filter(num_times_suggested__gte=num_times_suggested_threshold)\
                                           .annotate(like_score=F('num_times_liked')/F('num_times_suggested'))\
                                           .filter(like_score__gte=like_score_threshold)
                    not_suggested_enough_matches = price_filtered.filter(num_times_suggested__lt=num_times_suggested_threshold)
                    unattractive_matches = price_filtered.filter(num_times_suggested__gte=num_times_suggested_threshold)\
                                           .annotate(like_score=F('num_times_liked')/F('num_times_suggested'))\
                                           .filter(like_score__lt=like_score_threshold)
                    # Introduce randomness into these different groups of users and merge lists together so that attractive_matches
                    # are earlier in the list than not_suggested_enough_matches and unattractive_matches
                    attractive_matches = list(attractive_matches)
                    shuffle(attractive_matches)
                    not_suggested_enough_matches = list(not_suggested_enough_matches)
                    unattractive_matches = list(unattractive_matches)
                    not_suggested_enough_matches.extend(unattractive_matches)
                    shuffle(not_suggested_enough_matches)
                    attractive_matches.extend(not_suggested_enough_matches)
                    potential_matches = attractive_matches

                for potential_match in potential_matches:
                    # Calculate distance to place for each potential match
                    match_coordinates = (potential_match.latitude, potential_match.longitude)
                    place_coordinates = (place['coordinates']['latitude'], place['coordinates']['longitude'])
                    if great_circle(match_coordinates, place_coordinates).miles < potential_match.search_radius:
                        with transaction.atomic():
                            match = User.objects.select_for_update().get(pk=potential_match.pk)
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
                            # Exclude match if match already has a date for this day
                            if(getattr(match, day + '_date') and getattr(user, day + '_date').expires_at >= timezone.now()):
                                match = None
                                continue

                            # Generate an appropriate start time for date, taking into account user's times, match's
                            # times, category times, and open hours of the place
                            open_times = getPlaceHoursFromYelp(place['id'])
                            time = generateRandomTimeForDate(user, match, day, interests[category_index], open_times[day])

                            # Time will be None if the business, category time, user time and match time do not overlap
                            # for at least one hour
                            if not time:
                                match = None
                                continue

                            # Create date record and update user records
                            local_midnight = convertLocalTimeToUTC(
                                timezone.now().astimezone(pytz_timezone(user.timezone)).replace(hour=0, minute=0, second=0,
                                                                                           microsecond=0, tzinfo=None),
                                user.timezone)
                            date = models.Date(user1=user, user2=match, day=day, start_time=time,
                                               date_of_date=generateDateOfDateFromDay(day),
                                               expires_at=(local_midnight + datetime.timedelta(days=1)),
                                               place_id=place['id'],
                                               category=interests[category_index])
                            date.original_expires_at = date.expires_at
                            date.save()
                            setattr(user, day + '_date', date)
                            setattr(match, day + '_date', date)
                            user.num_times_suggested = user.num_times_suggested + 1
                            match.num_times_suggested = match.num_times_suggested + 1
                            user.save()
                            match.save()

                            # Get Mutual Friends
                            mutual_friends_json = facebook.getMutualFriends(user, potential_match)
                            if mutual_friends_json:
                                mutual_friends_json = mutual_friends_json['data']
                                for friend in mutual_friends_json:
                                    first_name = friend['name'].partition(' ')[0]
                                    date.mutualfriend_set.create(first_name=first_name,
                                                                 picture=friend['picture']['data']['url'])

                            return date

                if match or place_index == first_place_index:
                    break
                place_index = (place_index + 1) % len(places)

        if match or category_index == first_category_index:
            break
        category_index = (category_index + 1) % len(interests)

    if not match:
        return None

def convertDateToJson(user,date):

    # Add fields that don't have ambiguity around user
    json = {
        'date_id': date.pk,
        'respond_by': date.expires_at.replace(microsecond=0).astimezone(pytz_timezone(user.timezone)).isoformat(),
        'inspected_match': date.inspected_match,
        'date_of_date': date.date_of_date.isoformat(),
        'time':
            {
                'day': date.day,
                'start_time': date.start_time.isoformat()
            },
        'place':
            {
                'place_id': date.place_id,
            }
    }

    try:
        last_sent_message = date.message_set.order_by('-index')[0]
        json['last_sent_message'] = last_sent_message.content
        # If the user sent the message, we know he's read it. If the match sent the message, we look at the read field
        if last_sent_message.sent_by == user:
            json['message_read'] = True
        else:
            json['message_read'] = last_sent_message.read
    except IndexError:
        pass

    # Determine to which user the Date fields are relative
    if date.user1 == user:
        potential_match = date.user2
        # If potential match has passed, but the primary user has not been notified, tell client that the potential
        # match is undecided.
        if date.user2_likes == models.DateStatus.PASS.value and date.passed_user_notified == False:
            json['potential_match_likes'] = models.DateStatus.UNDECIDED.value
        else:
            json['potential_match_likes'] = date.user2_likes
        # If it's past the start time on the day of the date, it's a soft pass. The potential match will not show
        # up on the swipe screen, but they are not added to the passed_users list
        datetime_of_date = pytz_timezone(user.timezone).localize(datetime.datetime.combine(date.date_of_date, date.start_time))
        local_now = timezone.now().astimezone(pytz_timezone(user.timezone))
        if local_now >= datetime_of_date - datetime.timedelta(minutes=30) and date.user1_likes == models.DateStatus.UNDECIDED.value:
            json['primary_user_likes'] = models.DateStatus.PASS.value
        else:
            json['primary_user_likes'] = date.user1_likes
    else:
        potential_match = date.user1
        if date.user1_likes == models.DateStatus.PASS.value and date.passed_user_notified == False:
            json['potential_match_likes'] = models.DateStatus.UNDECIDED.value
        else:
            json['potential_match_likes'] = date.user1_likes
        # If it's past the start time on the day of the date, it's a soft pass. The potential match will not show
        # up on the swipe screen, but they are not added to the passed_users list
        datetime_of_date = pytz_timezone(user.timezone).localize(datetime.datetime.combine(date.date_of_date, date.start_time))
        local_now = timezone.now().astimezone(pytz_timezone(user.timezone))
        if local_now >= datetime_of_date - datetime.timedelta(minutes=30) and date.user2_likes == models.DateStatus.UNDECIDED.value:
            json['primary_user_likes'] = models.DateStatus.PASS.value
        else:
            json['primary_user_likes'] = date.user2_likes

    json['match'] = {
        'user_id': potential_match.pk,
        'name': potential_match.first_name,
        'age': potential_match.age,
        'occupation': potential_match.occupation,
        'education': potential_match.education,
        'gender': potential_match.gender,
        'about': potential_match.about,
        'main_picture': potential_match.picture1_portrait_url,
        'detail_pictures': [
            potential_match.picture1_square_url, potential_match.picture2_square_url, potential_match.picture3_square_url,
            potential_match.picture4_square_url, potential_match.picture5_square_url,
            potential_match.picture6_square_url
        ]
    }

    mutual_friends = []
    for friend in date.mutualfriend_set.all():
        mutual_friends.append({
            'friend': {
                'name': friend.first_name,
                'picture': friend.picture
            }
        })
    json['match']['mutual_friends'] = mutual_friends

    return json



#@csrf_exempt
#@custom_authenticate
def date(request, user, day):
    # If user does not have available time on this day, return None
    if not getattr(user, day + '_start_time') or not getattr(user, day + '_end_time'):
        return JsonResponse(json.dumps(None), safe=False)
    # If date already exists, return date
    if getattr(user, day + '_date') and getattr(user, day + '_date').expires_at >= timezone.now():
        return JsonResponse(convertDateToJson(user, getattr(user, day + '_date')), safe=False)
    else: # Query for a match and create date from those matches
        potential_matches = filterByUserStatus(User.objects.exclude(pk=user.pk))
        if user.is_fake_user: # Fake users should not match with other fake users
            potential_matches = filterFakeUsers(potential_matches)
        potential_matches = filterBySexualPreference(user, potential_matches)
        potential_matches = filterByAge(user, potential_matches)
        potential_matches = filterPassedMatches(user, potential_matches)
        potential_matches = filterTimeAvailableUsers(user, day, potential_matches)
        potential_matches = filterByLatitudeLongitude(user, potential_matches)
        makeDate(user, day, potential_matches)
        user = User.objects.get(pk=user.pk)
        if getattr(user, day + '_date'):
            return JsonResponse(convertDateToJson(user, getattr(user, day + '_date')), safe=False)
        else:
            return JsonResponse(json.dumps(None), safe=False)