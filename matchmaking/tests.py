import json

from django.test import TestCase
from model_mommy.recipe import Recipe, seq
from model_mommy import mommy
from api.models import User, Gender, SexualPreference
from matchmaking.views import filterBySexualPreference, filterPassedMatches, filterTimeAvailableUsers, makeDate,\
    generateRandomTimeForDate, date, generateDateOfDateFromDay, filterByAppropriateCategoryTimes
from matchmaking.yelp import getPlacesFromYelp
from matchmaking.models import YelpAccessToken, Date
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
        results = filterByAppropriateCategoryTimes(woman, time_filtered, day, 'nature')
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
        random_time = generateRandomTimeForDate(woman,man,'sun', 'drinks')
        self.assertEqual(random_time, man.sun_start_time)

        # Test if large range
        man.sun_start_time = time(hour=12, minute=0)
        man.sun_end_time = time(hour=22, minute=0)
        man.save()
        random_time = generateRandomTimeForDate(woman,man,'sun', 'drinks')
        self.assertGreaterEqual(random_time, woman.sun_start_time)
        self.assertLessEqual(random_time, time(hour=21, minute=0))

    def test_make_date(self):
        # Test when there are no category matches
        man = self.straight_men_users[0]
        man.likes_coffee = False
        man.latitude = 32.879001
        man.longitude = -96.717515
        man.search_radius = 24
        man.wed_start_time = time(hour=18, minute=30)
        man.wed_end_time = time(hour=22, minute=0)
        man.save()
        woman = self.straight_women_users[0]
        woman.likes_coffee = True
        woman.latitude = 32.897207
        woman.longitude = -96.746212
        woman.search_radius = 24
        woman.wed_start_time = time(hour=18, minute=30)
        woman.wed_end_time = time(hour=22, minute=0)
        woman.save()

        date = makeDate(woman, 'wed', User.objects.exclude(pk=woman.pk))
        self.assertEqual(date, None)

        # Test when there is a category match
        man.likes_coffee = True
        man.save()
        date = makeDate(woman, 'wed', User.objects.exclude(pk=woman.pk))
        man = User.objects.get(pk=man.pk)
        self.assertEqual(date.category, 'coffee')
        self.assertEqual(date.user1, woman)
        self.assertEqual(date.user2, man)
        self.assertEqual(date.day, 'wed')
        self.assertTrue(date.start_time >= woman.wed_start_time)
        self.assertTrue(date.start_time <= time(hour=21, minute=0))
        self.assertEqual(woman.wed_date, date)
        self.assertEqual(man.wed_date, date)

    def test_dates(self):
        # Man is our user making the request for dateslist
        man = self.straight_men_users[0]
        man.first_name = 'Joe'
        man.age = 28
        man.occupation = 'Musician'
        man.education = 'School of Hard Knocks'
        man.about = 'Nothing to see here'
        man.latitude = 32.8972250
        man.longitude = -96.7460090
        man.likes_coffee = True
        man.likes_nature = True
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
        man.fb_user_id = '110000369505832'
        man.most_recent_fb_auth_token = 'EAACEFGIZCorABAGsVlCIHsV815c9PTU1yT2iufkAbyiCn3yNb8MfczAqh7FPBt02s7k4yDVeI5TUac6sa1ylYbEZBl7oIVNjPtS4PopS7Oi7Mrgj4N9Lz7ND5036DziaEehKRdHUucvsNZC900v8YIp0pSagqWXBJyDNj74ZCl2whBDYJKPfrCRKXC4ZCFR3Xl45gXDZApa1ZCbfJvoNRnf'
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
        woman1.likes_nature = True
        woman1.sun_start_time = time(hour=18)
        woman1.sun_end_time = time(hour=23)
        woman1.fb_user_id = '131453847271362'
        woman1.most_recent_fb_auth_token = 'EAACEFGIZCorABAICptUHpj0A91yU3iJ6gVv97ZB3cChHZB6Md1OMOuIM9YWTC322NfmxuMV5Jt2FMlfZBS4Occ5ZApyZAWhC8aQgta5o7u2uGfvfCMn5Br3JXXtvZCt2pVBs5MJeJXMCZBUHjnJZCmaVlZAUF1oVZAao0pb3TZCfqyZB3B9QOaGMqryLnBDy9hLxNZAGVZAyNCQcgnqq4PQCZCNQT6GQ'
        woman1.save()
        dl = json.loads(json.loads(date(None, man, 'sun').content))
        self.assertEqual(dl['match']['name'], woman1.first_name)
        self.assertEqual(len(dl['match']['mutual_friends']), 2)
        d = Date.objects.first()
        self.assertEqual(len(d.mutualfriend_set.all()), 2)

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
        woman2.likes_nature = True
        woman2.sun_start_time = time(hour=18)
        woman2.sun_end_time = time(hour=23)
        woman2.save()
        dl = json.loads(json.loads(date(None, man, 'sun').content))
        self.assertEqual(dl['match']['name'], woman1.first_name)

        # woman2 should match because the date has expired woman1 is no longer matching on categories
        man.sun_date.expires_at = timezone.now() - timedelta(hours=25)
        man.sun_date.save()
        man.save()
        woman1.likes_coffee = False
        woman1.likes_nature = False
        woman1.save()
        dl = json.loads(json.loads(date(None, man, 'sun').content))
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
        woman3.likes_nature = True
        woman3.tue_start_time = time(hour=18)
        woman3.tue_end_time = time(hour=23)
        woman3.save()
        dl = json.loads(json.loads(date(None, man, 'tue').content))
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
        woman4.likes_active = True
        woman4.wed_start_time = time(hour=18)
        woman4.wed_end_time = time(hour=23)
        woman4.save()
        dl = json.loads(json.loads(date(None, man, 'wed').content))
        self.assertEqual(dl, None)

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
        dl = json.loads(json.loads(date(None, man, 'fri').content))
        self.assertEqual(dl, None)

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
        dl = json.loads(json.loads(date(None, man, 'sat').content))
        self.assertEqual(dl, None)


class YelpTestCase(TestCase):
    def setUp(self):
        self.user = mommy.make_recipe('api.user', likes_coffee=True, latitude=32.8972250, longitude=-96.7460090)
    def test_valid_request(self):
        pass
        list = getPlacesFromYelp(self.user, 'coffee')
        self.assertNotEqual(len(list), 0)
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
        list = getPlacesFromYelp(self.user, 'nature')
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


