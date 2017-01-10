from django.test import TestCase
from model_mommy.recipe import Recipe, seq
from model_mommy import mommy
from api.models import User, Gender, SexualPreference
from matchmaking.views import filterBySexualPreference, filterPassedMatches, filterTimeAvailableUsers, dayToDate
from matchmaking.yelp import getPlacesFromYelp
from matchmaking.models import YelpAccessToken
from datetime import datetime, timedelta, time

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
        count = filterBySexualPreference(self.straight_women_users[0]).count()
        self.assertEqual(count, len(self.straight_men_users)+len(self.bisexual_men_users))
        count = filterBySexualPreference(self.straight_men_users[0]).count()
        self.assertEqual(count, len(self.straight_women_users)+len(self.bisexual_women_users))
        count = filterBySexualPreference(self.lesbian_women_users[0]).count()
        self.assertEqual(count, len(self.lesbian_women_users)+len(self.bisexual_women_users) - 1) # Exclude self
        count = filterBySexualPreference(self.gay_men_users[0]).count()
        self.assertEqual(count, len(self.gay_men_users) + len(self.bisexual_men_users) - 1)  # Exclude self
        count = filterBySexualPreference(self.bisexual_men_users[0]).count()
        self.assertEqual(count, len(self.gay_men_users) + len(self.bisexual_men_users) +
                         len(self.straight_women_users) + len(self.bisexual_women_users) - 1)  # Exclude self
        count = filterBySexualPreference(self.bisexual_women_users[0]).count()
        self.assertEqual(count, len(self.straight_men_users) + len(self.bisexual_men_users) +
                         len(self.lesbian_women_users) + len(self.bisexual_women_users) - 1)  # Exclude self

    def test_passed_users_filter(self):
        self.straight_women_users[0].passed_matches.add(self.straight_men_users[0])
        self.straight_women_users[0].passed_matches.add(self.straight_men_users[1])
        self.straight_women_users[0].passed_matches.add(self.straight_men_users[2])
        self.straight_women_users[0].passed_matches.add(self.straight_men_users[3])
        self.straight_women_users[0].passed_matches.add(self.straight_men_users[4])
        count = filterPassedMatches(self.straight_women_users[0],User.objects.all()).count()
        self.assertEqual(User.objects.all().count()-self.straight_women_users[0].passed_matches.all().count(), count)

    def test_time_available_filter(self):
        # Test time overlapping
        woman = self.straight_women_users[0]
        woman.sunday_start_time = time(hour=18, minute=30)
        woman.sunday_end_time = time(hour=22, minute=0)
        woman.save()
        man = self.straight_men_users[0]
        man.sunday_start_time = time(hour=12, minute=0)
        man.sunday_end_time = time(hour=20, minute=0)
        man.save()
        results = filterTimeAvailableUsers(woman, User.objects.exclude(pk=woman.pk))
        self.assertEqual(results['sun'][0], man)

        # Test match time interval included in user time interval
        man.sunday_start_time = time(hour=19, minute=0)
        man.sunday_end_time = time(hour=20, minute=30)
        man.save()
        results = filterTimeAvailableUsers(woman, User.objects.exclude(pk=woman.pk))
        self.assertEqual(results['sun'][0], man)

        # Test user time interval included in match time interval
        man.sunday_start_time = time(hour=12, minute=0)
        man.sunday_end_time = time(hour=23, minute=30)
        man.save()
        results = filterTimeAvailableUsers(woman, User.objects.exclude(pk=woman.pk))
        self.assertEqual(results['sun'][0], man)

        # Test No overlap
        man.sunday_start_time = time(hour=12, minute=0)
        man.sunday_end_time = time(hour=18, minute=0)
        man.save()
        results = filterTimeAvailableUsers(woman, User.objects.exclude(pk=woman.pk))
        self.assertEqual(results['sun'].count(), 0)

        # Test overlap too short
        man.sunday_start_time = time(hour=12, minute=0)
        man.sunday_end_time = time(hour=18, minute=30)
        man.save()
        results = filterTimeAvailableUsers(woman, User.objects.exclude(pk=woman.pk))
        self.assertEqual(results['sun'].count(), 0)

    def test_day_to_date(self):
        # Test when there are no category matches
        man = self.straight_men_users[0]
        man.likes_coffee = False
        man.latitude = 32.879001
        man.longitude = -96.717515
        man.search_radius = 24
        man.save()
        woman = self.straight_women_users[0]
        woman.likes_coffee = True
        woman.latitude = 32.897207
        woman.longitude = -96.746212
        woman.search_radius = 24
        woman.save()

        date,place = dayToDate(woman, 'wed', User.objects.exclude(pk=woman.pk))
        self.assertEqual(date, None)
        self.assertEqual(place, None)

        # Test when there is a category match
        man.likes_coffee = True
        man.save()
        date, place = dayToDate(woman, 'wed', User.objects.exclude(pk=woman.pk))
        man = User.objects.get(pk=man.pk)
        self.assertEqual(date.category, 'coffee')
        self.assertEqual(date.user1, woman)
        self.assertEqual(date.user2, man)
        self.assertEqual(woman.wed_date, date)
        self.assertEqual(man.wed_date, date)
        #print(man.tue_date.pk)
        #print(woman.tue_date.pk)







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


