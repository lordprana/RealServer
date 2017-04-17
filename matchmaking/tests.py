import json
import mock
import pytz

from django.test import TestCase
from model_mommy.recipe import Recipe, seq
from model_mommy import mommy
from api.models import User, Gender, SexualPreference, Status
from matchmaking.views import filterBySexualPreference, filterPassedMatches, filterTimeAvailableUsers, makeDate,\
    generateRandomTimeForDate, date, generateDateOfDateFromDay, filterByAppropriateCategoryTimes, filterByLatitudeLongitude,\
    filterByUserStatus
from matchmaking.yelp import getPlacesFromYelp, getPlaceHoursFromYelp
from matchmaking.models import YelpAccessToken, Date, DateStatus, YelpBusinessHours
from datetime import datetime, timedelta, time
from django.utils import timezone

# Create your tests here.

class MatchMakingTestCase(TestCase):
    def setUp(self):
        self.straight_women_users = mommy.make_recipe('api.user', gender=Gender.WOMAN.value,
                                                      interested_in=SexualPreference.MEN.value,
                                                      _quantity=50)
        self.lesbian_women_users = mommy.make_recipe('api.user', gender=Gender.WOMAN.value,
                                                      interested_in=SexualPreference.WOMEN.value,
                                                     _quantity=10)
        self.bisexual_women_users = mommy.make_recipe('api.user', gender=Gender.WOMAN.value,
                                                     interested_in=SexualPreference.BISEXUAL.value,
                                                     _quantity=20)

        self.straight_men_users = mommy.make_recipe('api.user', gender=Gender.MAN.value,
                                                      interested_in=SexualPreference.WOMEN.value,
                                                      _quantity=60)
        self.gay_men_users = mommy.make_recipe('api.user', gender=Gender.MAN.value,
                                                    interested_in=SexualPreference.MEN.value,
                                                    _quantity=15)
        self.bisexual_men_users = mommy.make_recipe('api.user', gender=Gender.MAN.value,
                                                    interested_in=SexualPreference.BISEXUAL.value,
                                                    _quantity=25)
    def test_user_status_filter(self):
        woman1 = self.straight_women_users[0]
        woman1.status = Status.INACTIVE.value
        woman1.save()
        woman2 = self.straight_women_users[1]
        woman2.status = Status.INACTIVE.value
        woman2.save()
        count = filterByUserStatus(User.objects.filter(gender=Gender.WOMAN.value, interested_in=SexualPreference.MEN.value)).count()
        self.assertEqual(count, 48)

    def test_sexual_preference_filter(self):
        count = filterBySexualPreference(self.straight_women_users[0], User.objects.exclude(pk=self.straight_women_users[0].pk)).count()
        self.assertEqual(count, len(self.straight_men_users)+len(self.bisexual_men_users))
        count = filterBySexualPreference(self.straight_men_users[0], User.objects.exclude(pk=self.straight_men_users[0].pk)).count()
        self.assertEqual(count, len(self.straight_women_users)+len(self.bisexual_women_users))
        count = filterBySexualPreference(self.lesbian_women_users[0], User.objects.exclude(pk=self.lesbian_women_users[0].pk)).count()
        self.assertEqual(count, len(self.lesbian_women_users)+len(self.bisexual_women_users) - 1)
        count = filterBySexualPreference(self.gay_men_users[0], User.objects.exclude(pk=self.gay_men_users[0].pk)).count()
        self.assertEqual(count, len(self.gay_men_users) + len(self.bisexual_men_users) - 1)
        count = filterBySexualPreference(self.bisexual_men_users[0], User.objects.exclude(pk=self.bisexual_men_users[0].pk)).count()
        self.assertEqual(count, len(self.gay_men_users) + len(self.bisexual_men_users) +
                         len(self.straight_women_users) + len(self.bisexual_women_users) - 1)
        count = filterBySexualPreference(self.bisexual_women_users[0], User.objects.exclude(pk=self.bisexual_women_users[0].pk)).count()
        self.assertEqual(count, len(self.straight_men_users) + len(self.bisexual_men_users) +
                         len(self.lesbian_women_users) + len(self.bisexual_women_users) - 1)

    def test_passed_users_filter(self):
        self.straight_women_users[0].passed_matches.add(self.straight_men_users[0])
        self.straight_women_users[0].passed_matches.add(self.straight_men_users[1])
        self.straight_women_users[0].passed_matches.add(self.straight_men_users[2])
        self.straight_women_users[0].passed_matches.add(self.straight_men_users[3])
        self.straight_women_users[0].passed_matches.add(self.straight_men_users[4])

        count = filterPassedMatches(self.straight_women_users[0],User.objects.all()).count()
        self.assertEqual(User.objects.all().count()-self.straight_women_users[0].passed_matches.all().count(), count)
        self.assertEqual(self.straight_men_users[4].passed_matches.all().count(), 1)

    def test_time_available_filter(self):
        # Test time overlapping
        woman = self.straight_women_users[0]
        woman.sun_start_time = time(hour=18, minute=30)
        woman.sun_end_time = time(hour=22, minute=0)
        woman.save()
        man = self.straight_men_users[0]
        man.sun_start_time = time(hour=12, minute=0)
        man.sun_end_time = time(hour=20, minute=0)
        man.save()
        results = filterTimeAvailableUsers(woman, 'sun', User.objects.exclude(pk=woman.pk))
        self.assertEqual(results[0], man)

        # Test precise overlap
        man.sun_start_time = time(hour=18, minute=30)
        man.sun_end_time = time(hour=22, minute=0)
        man.save()
        results = filterTimeAvailableUsers(woman, 'sun', User.objects.exclude(pk=woman.pk))
        self.assertEqual(results[0], man)

        # Test match time interval included in user time interval
        man.sun_start_time = time(hour=19, minute=0)
        man.sun_end_time = time(hour=20, minute=30)
        man.save()
        results = filterTimeAvailableUsers(woman, 'sun', User.objects.exclude(pk=woman.pk))
        self.assertEqual(results[0], man)

        # Test user time interval included in match time interval
        man.sun_start_time = time(hour=12, minute=0)
        man.sun_end_time = time(hour=23, minute=30)
        man.save()
        results = filterTimeAvailableUsers(woman, 'sun', User.objects.exclude(pk=woman.pk))
        self.assertEqual(results[0], man)

        # Test only one hour in match time interval
        man.sun_start_time = time(hour=21, minute=0)
        man.sun_end_time = time(hour=22, minute=0)
        man.save()
        results = filterTimeAvailableUsers(woman, 'sun', User.objects.exclude(pk=woman.pk))
        self.assertEqual(results[0], man)

        # Test No overlap
        man.sun_start_time = time(hour=12, minute=0)
        man.sun_end_time = time(hour=18, minute=0)
        man.save()
        results = filterTimeAvailableUsers(woman, 'sun', User.objects.exclude(pk=woman.pk))
        self.assertEqual(results.count(), 0)

        # Test overlap too short
        man.sun_start_time = time(hour=12, minute=0)
        man.sun_end_time = time(hour=18, minute=30)
        man.save()
        results = filterTimeAvailableUsers(woman, 'sun', User.objects.exclude(pk=woman.pk))
        self.assertEqual(results.count(), 0)

    def test_latitude_longitude_filter(self):
        woman = self.straight_women_users[0]
        woman.latitude = 45.77
        woman.longitude = -68.43
        woman.save()
        # Create man that will not be filtered
        man1 = self.straight_men_users[0]
        man1.latitude = 46.38
        man1.longitude = -68.44
        man1.save()
        # Create men that will be filtered
        man2 = self.straight_men_users[1]
        man2.latitude = 42.87
        man2.longitude = -68.43
        man2.save()
        man3 = self.straight_men_users[2]
        man3.latitude = 45.76
        man3.longitude = -69.53
        man3.save()
        results = filterByLatitudeLongitude(woman, User.objects.exclude(pk=woman.pk))
        self.assertEqual(results.count(), 1)

    def test_appropriate_category_times_filter(self):
        # Test appropriate time
        woman = self.straight_women_users[0]
        woman.sun_start_time = time(hour=18, minute=30)
        woman.sun_end_time = time(hour=22, minute=0)
        woman.save()
        man = self.straight_men_users[0]
        man.sun_start_time = time(hour=12, minute=0)
        man.sun_end_time = time(hour=20, minute=0)
        man.save()
        day = 'sun'
        time_filtered = filterTimeAvailableUsers(woman, day, User.objects.exclude(pk=woman.pk))
        results = filterByAppropriateCategoryTimes(woman, time_filtered, day, 'drinks')
        self.assertEqual(results[0], man)

        # Test primary user inappropriate time
        woman = self.straight_women_users[0]
        woman.fri_start_time = time(hour=18, minute=30)
        woman.fri_end_time = time(hour=22, minute=0)
        woman.save()
        man = self.straight_men_users[0]
        man.fri_start_time = time(hour=12, minute=0)
        man.fri_end_time = time(hour=20, minute=0)
        man.save()
        day = 'fri'
        time_filtered = filterTimeAvailableUsers(woman, day, User.objects.exclude(pk=woman.pk))
        results = filterByAppropriateCategoryTimes(woman, time_filtered, day, 'parks')
        self.assertEqual(results.count(), 0)

        # Test potential match inappropriate time
        woman = self.straight_women_users[0]
        woman.mon_start_time = time(hour=18, minute=30)
        woman.mon_end_time = time(hour=22, minute=0)
        woman.save()
        man = self.straight_men_users[0]
        man.mon_start_time = time(hour=20, minute=0)
        man.mon_end_time = time(hour=23, minute=0)
        man.save()
        day = 'mon'
        time_filtered = filterTimeAvailableUsers(woman, day, User.objects.exclude(pk=woman.pk))
        results = filterByAppropriateCategoryTimes(woman, time_filtered, day, 'coffee')
        self.assertEqual(results.count(), 0)

    def test_generate_date_of_date_from_day(self):
        # This test must be rewritten for current time
        date = generateDateOfDateFromDay('thur')
        self.assertEqual(date.day, 26)
        self.assertEqual(date.month, 1)
        date = generateDateOfDateFromDay('mon')
        self.assertEqual(date.day, 30)
        self.assertEqual(date.month, 1)
        date = generateDateOfDateFromDay('wed')
        self.assertEqual(date.day, 1)
        self.assertEqual(date.month, 2)

    def test_generate_random_time_for_date(self):
        # Test if only an hour window
        woman = self.straight_women_users[0]
        woman.sun_start_time = time(hour=18, minute=30)
        woman.sun_end_time = time(hour=22, minute=0)
        woman.save()
        man = self.straight_men_users[0]
        man.sun_start_time = time(hour=21, minute=0)
        man.sun_end_time = time(hour=22, minute=0)
        man.save()
        open_times = getPlaceHoursFromYelp('barcadia-dallas')
        random_time = generateRandomTimeForDate(woman,man,'sun', 'drinks', open_times)
        self.assertEqual(random_time, man.sun_start_time)

        # Test if large range
        man.sun_start_time = time(hour=12, minute=0)
        man.sun_end_time = time(hour=22, minute=0)
        man.save()
        open_times = getPlaceHoursFromYelp('barcadia-dallas')
        random_time = generateRandomTimeForDate(woman,man,'sun', 'drinks', open_times)
        self.assertGreaterEqual(random_time, woman.sun_start_time)
        self.assertLessEqual(random_time, time(hour=21, minute=0))

        # Test if place is not open on that day
        woman.mon_start_time = time(hour=12, minute=30)
        woman.mon_end_time = time(hour=22, minute=0)
        woman.save()
        man.mon_start_time = time(hour=12, minute=30)
        man.mon_end_time = time(hour=22, minute=0)
        man.save()

        open_times = getPlaceHoursFromYelp('dallas-museum-of-art-dallas')
        random_time = generateRandomTimeForDate(woman, man, 'mon', 'museums', open_times)
        self.assertEqual(random_time, None)

        # Test if times are not compatible
        woman.tue_start_time = time(hour=18, minute=30)
        woman.tue_end_time = time(hour=22, minute=0)
        woman.save()
        man.tue_start_time = time(hour=21, minute=0)
        man.tue_end_time = time(hour=22, minute=0)
        man.save()
        open_times = getPlaceHoursFromYelp('dallas-museum-of-art-dallas')
        random_time = generateRandomTimeForDate(woman, man, 'tue', 'museums', open_times)
        self.assertEqual(random_time, None)

        # Test if times are not compatible, but there is 30 minutes of overlap
        woman.tue_start_time = time(hour=16, minute=30)
        woman.tue_end_time = time(hour=22, minute=0)
        woman.save()
        man.tue_start_time = time(hour=12, minute=0)
        man.tue_end_time = time(hour=22, minute=0)
        man.save()
        open_times = getPlaceHoursFromYelp('dallas-museum-of-art-dallas')
        random_time = generateRandomTimeForDate(woman, man, 'tue', 'museums', open_times)
        self.assertEqual(random_time, None)

        # Test if place has no hours (always open)
        woman.tue_start_time = time(hour=12, minute=30)
        woman.tue_end_time = time(hour=22, minute=0)
        woman.save()
        man.tue_start_time = time(hour=13, minute=0)
        man.tue_end_time = time(hour=22, minute=0)
        man.save()
        open_times = getPlaceHoursFromYelp('white-rock-lake-dallas')
        random_time = generateRandomTimeForDate(woman, man, 'tue', 'parks', open_times)
        self.assertGreaterEqual(random_time, man.tue_start_time)
        self.assertLessEqual(random_time, time(hour=19, minute=0))

    def test_make_date(self):
        # Test when there are no category matches
        man = self.straight_men_users[0]
        man.likes_coffee = False
        man.latitude = 32.879001
        man.longitude = -96.717515
        man.search_radius = 24
        man.wed_start_time = time(hour=18, minute=30)
        man.wed_end_time = time(hour=22, minute=0)
        man.timezone = 'US/Eastern'
        man.save()
        woman = self.straight_women_users[0]
        woman.likes_coffee = True
        woman.latitude = 32.897207
        woman.longitude = -96.746212
        woman.search_radius = 24
        woman.wed_start_time = time(hour=18, minute=30)
        woman.wed_end_time = time(hour=22, minute=0)
        woman.timezone = 'US/Eastern'
        woman.save()

        date = makeDate(woman, 'wed', User.objects.exclude(pk=woman.pk))
        self.assertEqual(date, None)

        # Test when there is a category match
        man.likes_coffee = True
        man.save()
        date = makeDate(woman, 'wed', User.objects.exclude(pk=woman.pk))
        man = User.objects.get(pk=man.pk)
        woman = User.objects.get(pk=woman.pk)
        self.assertEqual(date.category, 'coffee')
        self.assertEqual(date.user1, woman)
        self.assertEqual(date.user2, man)
        self.assertEqual(date.day, 'wed')
        # timezone.now() is UTC. User timezone is US/Eastern. To reconcile, we must make the hour of timezone.now() 5.
        self.assertEqual(date.expires_at, (timezone.now() + timedelta(days=1)).replace(hour=5, minute=0,
                                                                                            second=0, microsecond=0))
        self.assertEqual(date.original_expires_at, (timezone.now() + timedelta(days=1)).replace(hour=5, minute=0,
                                                                                            second=0, microsecond=0))
        self.assertTrue(date.start_time >= woman.wed_start_time)
        self.assertTrue(date.start_time <= time(hour=21, minute=0))
        self.assertEqual(woman.wed_date, date)
        self.assertEqual(man.wed_date, date)

    def test_dates(self):

        # Man is our user making the request for dates
        man = self.straight_men_users[0]
        man.first_name = 'Joe'
        man.age = 28
        man.occupation = 'Musician'
        man.education = 'School of Hard Knocks'
        man.about = 'Nothing to see here'
        man.latitude = 32.8972250
        man.longitude = -96.7460090
        man.likes_coffee = True
        man.likes_parks = True
        man.sun_start_time = time(hour=18)
        man.sun_end_time = time(hour=23)
        man.mon_start_time = time(hour=18)
        man.mon_end_time = time(hour=23)
        man.tue_start_time = time(hour=18)
        man.tue_end_time = time(hour=23)
        man.wed_start_time = time(hour=18)
        man.wed_end_time = time(hour=23)
        man.thur_start_time = time(hour=18)
        man.thur_end_time = time(hour=23)
        man.fri_start_time = time(hour=18)
        man.fri_end_time = time(hour=23)
        man.sat_start_time = time(hour=18)
        man.sat_end_time = time(hour=23)
        man.timezone = 'US/Central'
        man.fb_user_id = '110000369505832'
        man.most_recent_fb_auth_token = 'EAACEFGIZCorABAG3n2WADdNR6v93KP1XdbZCev1GEZCW7KdFYavc2RlpYNEJYhR1pGRPXIphJhZCqBx5x6TyjfkkoGSzWZB3T0po4CbPZBnzh3d2WVmCoIvQboMrZAQ2DfftMezZAc3rpPA6ADBjQ1woZBGyf4dWRsUSpcohoR20jsoFZABfaHLQ9cn0ohL29lzUFR4UOJ8lg2RokImY9vyiBC'
        man.save()

        # Create man's matches

        # woman1 should match with man
        woman1 = self.straight_women_users[0]
        woman1.first_name = 'Hailey'
        woman1.age = 28
        woman1.occupation = 'Waitress'
        woman1.education = ''
        woman1.about = 'Nothing to see here'
        woman1.latitude = 32.8972250
        woman1.longitude = -96.7460090
        woman1.likes_coffee = True
        woman1.likes_parks = True
        woman1.sun_start_time = time(hour=18)
        woman1.sun_end_time = time(hour=23)
        woman1.timezone = 'US/Central'
        woman1.fb_user_id = '131453847271362'
        woman1.most_recent_fb_auth_token = 'EAACEFGIZCorABAAfLLjpjlMhlwlP55xu7ZBhPWQkz3lEZAyZABCzjzdZBZBIAAKpZCyB24uzGhqFr4lDJyNvp6MbgC0S5MFF0e8cxI80VI6B6d1lfmxJuPviqu1y7v8bpDUYeEt6pSPc4Ex9e4ViJzMJHliTByCPapEfDxnkRc4rHjWwQqI7IFc8pXmKuEzT6KlCd6x2jlvRW32d38QZAoNq'
        woman1.save()
        dl = json.loads(date(None, man, 'sun').content)
        self.assertEqual(dl['match']['name'], woman1.first_name)
        #self.assertEqual(len(dl['match']['mutual_friends']), 2) # This causes tests to fail unless we refresh woman1's fb auth token
        self.assertEqual(dl['potential_match_likes'], DateStatus.UNDECIDED.value)
        self.assertEqual(dl['primary_user_likes'], DateStatus.UNDECIDED.value)
        d = Date.objects.first()
        #self.assertEqual(len(d.mutualfriend_set.all()), 2) # This causes tests to fail unless we refresh woman1's fb auth token

        # Test value of potential_match_likes in convertDateToJson is being set correctly
        d.user2_likes = DateStatus.PASS.value
        d.save()
        man = User.objects.get(pk=man.pk)
        dl = json.loads(date(None, man, 'sun').content)
        self.assertEqual(dl['potential_match_likes'], DateStatus.UNDECIDED.value)
        d.passed_user_notified = True
        d.save()
        man = User.objects.get(pk=man.pk)
        dl = json.loads(date(None, man, 'sun').content)
        self.assertEqual(dl['potential_match_likes'], DateStatus.PASS.value)

        # Test correct behavior for when date starts before the current time. Should return a PASS for primary user likes.
        man2 = self.straight_men_users[1]
        man2.first_name = 'Joe'
        man2.age = 28
        man2.occupation = 'Musician'
        man2.education = 'School of Hard Knocks'
        man2.about = 'Nothing to see here'
        man2.latitude = 32.8972250
        man2.longitude = -96.7460090
        man2.likes_coffee = True
        man2.likes_parks = True
        man2.mon_start_time = time(hour=12)
        man2.mon_end_time = time(hour=13)
        man2.timezone = 'US/Central'
        man2.fb_user_id = '110000369505843'
        man2.most_recent_fb_auth_token = 'EAACEFGIZCorABAG3n2WADdNR6v93KP1XdbZCev1GEZCW7KdFYavc2RlpYNEJYhR1pGRPXIphJhZCqBx5x6TyjfkkoGSzWZB3T0po4CbPZBnzh3d2WVmCoIvQboMrZAQ2DfftMezZAc3rpPA6ADBjQ1woZBGyf4dWRsUSpcohoR20jsoFZABfaHLQ9cn0ohL29lzUFR4UOJ8lg2RokImY9vyiBC'
        man2.save()

        woman1.mon_start_time = time(hour=12)
        woman1.mon_end_time = time(hour=13)
        woman1.save()
        # Now is late enough that after timezone conversion, it is still greater than the date start time
        NOW_FOR_TESTING = datetime(year=2017, month=1, day=23, hour=19, minute=0, second=0, tzinfo=pytz.utc)
        def mocked_now():
            return NOW_FOR_TESTING
        with mock.patch('django.utils.timezone.now', side_effect=mocked_now):
            dl = json.loads(date(None, man2, 'mon').content)
            self.assertEqual(dl['primary_user_likes'], DateStatus.PASS.value)

        # Now is not late enough, so after timezone conversion, the hour is less than the date start time, so no soft pass
        NOW_FOR_TESTING = datetime(year=2017, month=1, day=23, hour=15, minute=0, second=0, tzinfo=pytz.utc)
        def mocked_now():
            return NOW_FOR_TESTING
        with mock.patch('django.utils.timezone.now', side_effect=mocked_now):
            dl = json.loads(date(None, man2, 'mon').content)
            self.assertEqual(dl['primary_user_likes'], DateStatus.UNDECIDED.value)


        # woman2 shouldn't match because man already has date with woman1
        woman2 = self.straight_women_users[1]
        woman2.first_name = 'Natalie'
        woman2.age = 27
        woman2.occupation = 'Waitress'
        woman2.education = ''
        woman2.about = 'Nothing to see here'
        woman2.latitude = 32.8972250
        woman2.longitude = -96.7460090
        woman2.likes_coffee = True
        woman2.likes_parks = True
        woman2.sun_start_time = time(hour=18)
        woman2.sun_end_time = time(hour=23)
        woman2.save()
        dl = json.loads(date(None, man, 'sun').content)
        self.assertEqual(dl['match']['name'], woman1.first_name)

        # woman2 should match because the date has expired woman1 is no longer matching on categories
        man.sun_date.expires_at = timezone.now() - timedelta(hours=25)
        man.sun_date.save()
        man.save()
        woman1.likes_coffee = False
        woman1.likes_parks = False
        woman1.save()
        dl = json.loads(date(None, man, 'sun').content)
        self.assertEqual(dl['match']['name'], woman2.first_name)

        # woman3 should match because it's a different day
        woman3 = self.straight_women_users[2]
        woman3.first_name = 'Christina'
        woman3.age = 27
        woman3.occupation = 'Waitress'
        woman3.education = ''
        woman3.about = 'Nothing to see here'
        woman3.latitude = 32.8972250
        woman3.longitude = -96.7460090
        woman3.likes_coffee = True
        woman3.likes_parks = True
        woman3.tue_start_time = time(hour=18)
        woman3.tue_end_time = time(hour=23)
        woman3.save()
        dl = json.loads(date(None, man, 'tue').content)
        self.assertEqual(dl['match']['name'], woman3.first_name)

        # woman 4 shouldn't match because she doesn't like the same categories
        woman4 = self.straight_women_users[3]
        woman4.name = 'Zoe'
        woman4.age = 27
        woman4.occupation = 'Waitress'
        woman4.education = ''
        woman4.about = 'Nothing to see here'
        woman4.latitude = 32.8972250
        woman4.longitude = -96.7460090
        woman4.likes_fun = True
        woman4.wed_start_time = time(hour=18)
        woman4.wed_end_time = time(hour=23)
        woman4.save()
        dl = json.loads(date(None, man, 'wed').content)
        self.assertEqual(dl, 'null')

        # woman 6 shouldn't match because she is in another city
        woman6 = self.straight_women_users[5]
        woman6.first_name = 'Christa'
        woman6.age = 27
        woman6.occupation = 'Waitress'
        woman6.education = ''
        woman6.about = 'Nothing to see here'
        woman6.latitude = 30.263946
        woman6.longitude = -97.695592
        woman6.likes_coffee = True
        woman6.fri_start_time = time(hour=18)
        woman6.fri_end_time = time(hour=23)
        woman6.save()
        dl = json.loads(date(None, man, 'fri').content)
        self.assertEqual(dl, 'null')

        # woman 7 shouldn't match because she's not free at the right times
        woman7 = self.straight_women_users[6]
        woman7.first_name = 'Melanie'
        woman7.age = 27
        woman7.occupation = 'Waitress'
        woman7.education = ''
        woman7.about = 'Nothing to see here'
        woman7.latitude = 32.8972250
        woman7.longitude = -96.7460090
        woman7.likes_coffee = True
        woman7.sat_start_time = time(hour=16)
        woman7.sat_end_time = time(hour=18, minute=30)
        woman7.save()
        dl = json.loads(date(None, man, 'sat').content)
        self.assertEqual(dl, 'null')


class YelpTestCase(TestCase):
    def setUp(self):
        self.user = mommy.make_recipe('api.user', likes_coffee=True, latitude=32.8972250, longitude=-96.7460090)
    def test_get_places_from_yelp(self):
        # Test valid request
        list = getPlacesFromYelp(self.user, 'coffee')
        self.assertNotEqual(len(list), 0)
        # Test request with no recomendations in area
        self.not_yelp_user = mommy.make_recipe('api.user', likes_coffee=True, latitude=49.9935, longitude=36.2304)
        list = getPlacesFromYelp(self.not_yelp_user, 'coffee')
        self.assertEqual(len(list), 0)
    def test_price_limit(self):
        self.user.max_price = 4
        self.user.save()
        list = getPlacesFromYelp(self.user, 'food')
        four_price = False
        for l in list:
            if l.get('price', None) == '$$$$':
                four_price = True
        self.assertEqual(four_price,True)

        self.user.max_price = 3
        self.user.save()
        list = getPlacesFromYelp(self.user, 'food')
        for l in list:
            if l.get('price', None) == '$$$$':
                self.fail('Business list should not contain $$$$')
        self.user.max_price = 2
        self.user.save()
        list = getPlacesFromYelp(self.user, 'food')
        for l in list:
            if l.get('price', None) == '$$$$' or l.get('price', None) == '$$$':
                self.fail('Business list should not contain $$$ or $$$$')
        self.user.max_price = 1
        self.user.save()
        list = getPlacesFromYelp(self.user, 'food')
        for l in list:
            if l.get('price', None) == '$$$$' or l.get('price', None) == '$$$' or l.get('price', None) == '$$':
                self.fail('Business list should not contain $$ or $$$ or $$$$')
        self.user.max_price = 0
        self.user.save()
        list = getPlacesFromYelp(self.user, 'parks')
        for l in list:
            if l.get('price', None) == '$$$$' or l.get('price', None) == '$$$' or l.get('price', None) == '$$' or\
                            l.get('price', None) == '$':
                self.fail('Business list should not contain $ or $$ or $$$ or $$$$')

    def test_auth_token_renewal(self):
        # Test auth token creation
        self.assertEqual(YelpAccessToken.objects.all().count(), 0)
        list = getPlacesFromYelp(self.user, 'coffee')
        self.assertNotEqual(len(list), 0)
        self.assertEqual(YelpAccessToken.objects.all().count(), 1)

        # Test subsequent calls do not create new auth token
        list = getPlacesFromYelp(self.user, 'coffee')
        self.assertNotEqual(len(list), 0)
        self.assertEqual(YelpAccessToken.objects.all().count(), 1)

        # Test expired token causes new token refresh
        token = YelpAccessToken.objects.all()[0]
        token.expires_at = token.expires_at - timedelta(days=360)
        token.save()
        list = getPlacesFromYelp(self.user, 'coffee')
        self.assertNotEqual(len(list), 0)
        self.assertEqual(YelpAccessToken.objects.all().count(), 2)

    def test_get_place_hours(self):
        # Request of place id 'meadows-museum-dallas'
        request_json = {u'is_claimed': True, u'rating': 4.5, u'review_count': 23, u'name': u'Meadows Museum', u'photos': [u'https://s3-media3.fl.yelpcdn.com/bphoto/swJAMC7-34PxByWT-ZmwBw/o.jpg', u'https://s3-media4.fl.yelpcdn.com/bphoto/-QVXX9eaMO50koRcItldWw/o.jpg', u'https://s3-media1.fl.yelpcdn.com/bphoto/fQ3b_iP7e9EchVqmJNFc7Q/o.jpg'], u'url': u'https://www.yelp.com/biz/meadows-museum-dallas?adjust_creative=s7-DcAMdseJJmTHuki81Wg&utm_campaign=yelp_api_v3&utm_medium=api_v3_business_lookup&utm_source=s7-DcAMdseJJmTHuki81Wg', u'transactions': [], u'coordinates': {u'latitude': 32.8397891146511, u'longitude': -96.7795944213867}, u'hours': [{u'hours_type': u'REGULAR', u'open': [{u'is_overnight': False, u'end': u'1700', u'day': 1, u'start': u'1000'}, {u'is_overnight': False, u'end': u'1700', u'day': 2, u'start': u'1000'}, {u'is_overnight': False, u'end': u'2100', u'day': 3, u'start': u'1000'}, {u'is_overnight': False, u'end': u'1700', u'day': 4, u'start': u'1000'}, {u'is_overnight': False, u'end': u'1700', u'day': 5, u'start': u'1000'}, {u'is_overnight': False, u'end': u'1700', u'day': 6, u'start': u'1300'}], u'is_open_now': False}], u'phone': u'+12147682516', u'image_url': u'https://s3-media3.fl.yelpcdn.com/bphoto/swJAMC7-34PxByWT-ZmwBw/o.jpg', u'categories': [{u'alias': u'museums', u'title': u'Museums'}], u'display_phone': u'(214) 768-2516', u'id': u'meadows-museum-dallas', u'is_closed': False, u'location': {u'cross_streets': u'', u'city': u'Dallas', u'display_address': [u'5900 Bishop Blvd', u'Southern Methodist University', u'Dallas, TX 75205'], u'country': u'US', u'address2': u'', u'address3': u'Southern Methodist University', u'state': u'TX', u'address1': u'5900 Bishop Blvd', u'zip_code': u'75205'}}
        class MockedResponse(object):
            def json(self):
                return request_json
            status_code = 200
        def mocked_get(a, headers=None):
            return MockedResponse()
        with mock.patch('requests.get', side_effect=mocked_get) as request_call_count:
            place_id = 'meadows-museum-dallas'
            self.assertEqual(YelpBusinessHours.objects.filter(place_id=place_id).count(), 0)
            getPlaceHoursFromYelp(place_id)
            self.assertEqual(request_call_count.call_count, 1)
            self.assertEqual(YelpBusinessHours.objects.filter(place_id=place_id).count(), 1)
            hours = YelpBusinessHours.objects.get(place_id=place_id)
            self.assertEqual(hours.mon_start_time, None)
            self.assertEqual(hours.mon_end_time, None)
            self.assertEqual(hours.tue_start_time, time(hour=10))
            self.assertEqual(hours.tue_end_time, time(hour=17))
            self.assertEqual(hours.wed_start_time, time(hour=10))
            self.assertEqual(hours.wed_end_time, time(hour=17))
            self.assertEqual(hours.thur_start_time, time(hour=10))
            self.assertEqual(hours.thur_end_time, time(hour=21))
            self.assertEqual(hours.fri_start_time, time(hour=10))
            self.assertEqual(hours.fri_end_time, time(hour=17))
            self.assertEqual(hours.sat_start_time, time(hour=10))
            self.assertEqual(hours.sat_end_time, time(hour=17))
            self.assertEqual(hours.sun_start_time, time(hour=13))
            self.assertEqual(hours.sun_end_time, time(hour=17))

            # Ensure request is not called again, now that place_id entry exists in database
            getPlaceHoursFromYelp(place_id)
            self.assertEqual(request_call_count.call_count, 1)





