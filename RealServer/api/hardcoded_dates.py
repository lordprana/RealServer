from datetime import datetime

date1 = {
    'Date':
        {
            'date_id': '1',
            'target_likes': False,
            'primary_user_likes': 'undecided',
            'User':
                {
                    'user_id': '1',
                    'name': 'Matthew',
                    'age': '27',
                    'occupation': 'World Traveler',
                    'education': 'Yale University',
                    'about': 'I\'m trying to be clever.',
                    'main_picture': 'http://127.0.0.1:8000/media/Matthew_image.png',
                    'additional_pictures': [
                        'http://127.0.0.1:8000/media/Matthew_image_2.png',
                        'http://127.0.0.1:8000/media/Matthew_image_3.png'
                    ],
                    'mutual_friends': [
                        {'friend':
                             {
                                 'name': 'Anthony',
                                 'picture': 'http://127.0.0.1:8000/media/60x60_anthony.png'
                             }
                         }
                    ]
                },
            'time':
                {
                    'day': 'Tue',
                    'start_time': '7:00pm'
                },
            'place':
                {
                    'place_id': '1',
                    'name': 'Barcadia',
                    'latitude': 32.81169,
                    'longitude': -96.775201,
                    'price': 2,
                    'rating': 4.5,
                    'review_count': 327,
                    'phone': '(214) 721-7300',
                    'photos': [
                        'http://127.0.0.1:8000/media/Barcadia_image.png',
                        'http://127.0.0.1:8000/media/Barcadia_image_2.png',
                    ],
                    'category': 'Drinks',
                    'address1': '1917 N Henderson Ave'
                }
        }
    }

date2 = {
    'Date':
        {
            'date_id': '2',
            'target_likes': True,
            'primary_user_likes': 'undecided',
            'User':
                {
                    'user_id': '2',
                    'name': 'Anthony',
                    'age': '28',
                    'occupation': 'Actor',
                    'education': 'University of North Texas',
                    'about': 'I\'m a kind and sweet gentleman. Everything I do is motivated by the desire to help other people. I\'m an actor and I love my craft. Everytime I go outside I think to myself, "Today is a day to be different. Today is a day to be great." I\'m from Dallas to NYC. Ever since I was born I knew I would be a great person. My mom taught me the power of belief. Now I know this is my super power.',
                    'main_picture': 'http://127.0.0.1:8000/media/Anthony_image.png',
                    'additional_pictures': [
                        'http://127.0.0.1:8000/media/Anthony_image_2.png',
                    ],
                    'mutual_friends': [
                        {'friend':
                             {
                                 'name': 'Matthew',
                                 'picture': 'http://127.0.0.1:8000/media/60x60_matthew.png'
                             }
                         }
                    ]
                },
            'time':
                {
                    'day': 'Wed',
                    'start_time': '9:00pm'
                },
            'place':
                {
                    'place_id': '2',
                    'name': 'White Rock Lake',
                    'latitude': 32.828066,
                    'longitude': -96.725316,
                    'price': 0,
                    'rating': 4.5,
                    'review_count': 199,
                    'phone': None,
                    'photos': [
                        'http://127.0.0.1:8000/media/White_rock_lake_image.png',
                        'http://127.0.0.1:8000/media/White_rock_lake_image_2.png',
                    ],
                    'category': 'Nature',
                    'address1': None
                }
        }
    }

date3 = {
    'Date':
        {
            'date_id': '3',
            'target_likes': False,
            'primary_user_likes': 'undecided',
            'User':
                {
                    'user_id': '1',
                    'name': 'Matthew',
                    'age': '27',
                    'occupation': 'World Traveler',
                    'education': 'Yale University',
                    'about': 'I\'m trying to be clever.',
                    'main_picture': 'http://127.0.0.1:8000/media/Matthew_image.png',
                    'additional_pictures': [
                        'http://127.0.0.1:8000/media/Matthew_image_2.png',
                        'http://127.0.0.1:8000/media/Matthew_image_3.png'
                    ],
                    'mutual_friends': [
                        {'friend':
                             {
                                 'name': 'Anthony',
                                 'picture': 'http://127.0.0.1:8000/media/60x60_anthony.png'
                             }
                         }
                    ]
                },
            'time':
                {
                    'day': 'Thur',
                    'start_time': '12:00pm'
                },
            'place':
                {
                    'place_id': '1',
                    'name': 'Barcadia',
                    'latitude': 32.81169,
                    'longitude': -96.775201,
                    'price': 2,
                    'rating': 4.5,
                    'review_count': 327,
                    'phone': '(214) 721-7300',
                    'photos': [
                        'http://127.0.0.1:8000/media/Barcadia_image.png',
                        'http://127.0.0.1:8000/media/Barcadia_image_2.png',
                    ],
                    'category': 'Drinks',
                    'address1': '1917 N Henderson Ave'
                }
        }
    }

date4 = {
    'Date':
        {
            'date_id': '4',
            'target_likes': True,
            'primary_user_likes': 'undecided',
            'User':
                {
                    'user_id': '2',
                    'name': 'Anthony',
                    'age': '28',
                    'occupation': 'Actor',
                    'education': 'University of North Texas',
                    'about': 'I\'m a kind and sweet gentleman. Everything I do is motivated by the desire to help other people. I\'m an actor and I love my craft. Everytime I go outside I think to myself, "Today is a day to be different. Today is a day to be great." I\'m from Dallas to NYC. Ever since I was born I knew I would be a great person. My mom taught me the power of belief. Now I know this is my super power.',
                    'main_picture': 'http://127.0.0.1:8000/media/Anthony_image.png',
                    'additional_pictures': [
                        'http://127.0.0.1:8000/media/Anthony_image_2.png',
                    ],
                    'mutual_friends': [
                        {'friend':
                             {
                                 'name': 'Matthew',
                                 'picture': 'http://127.0.0.1:8000/media/60x60_matthew.png'
                             }
                         }
                    ]
                },
            'time':
                {
                    'day': 'Fri',
                    'start_time': '10:00am'
                },
            'place':
                {
                    'place_id': '2',
                    'name': 'White Rock Lake',
                    'latitude': 32.828066,
                    'longitude': -96.725316,
                    'price': 0,
                    'rating': 4.5,
                    'review_count': 199,
                    'phone': None,
                    'photos': [
                        'http://127.0.0.1:8000/media/White_rock_lake_image.png',
                        'http://127.0.0.1:8000/media/White_rock_lake_image_2.png',
                    ],
                    'category': 'Nature',
                    'address1': None
                }
        }
    }

date5 = {
    'Date':
        {
            'date_id': '5',
            'target_likes': False,
            'primary_user_likes': 'undecided',
            'User':
                {
                    'user_id': '1',
                    'name': 'Matthew',
                    'age': '27',
                    'occupation': 'World Traveler',
                    'education': 'Yale University',
                    'about': 'I\'m trying to be clever.',
                    'main_picture': 'http://127.0.0.1:8000/media/Matthew_image.png',
                    'additional_pictures': [
                        'http://127.0.0.1:8000/media/Matthew_image_2.png',
                        'http://127.0.0.1:8000/media/Matthew_image_3.png'
                    ],
                    'mutual_friends': [
                        {'friend':
                             {
                                 'name': 'Anthony',
                                 'picture': 'http://127.0.0.1:8000/media/60x60_anthony.png'
                             }
                         }
                    ]
                },
            'time':
                {
                    'day': 'Sat',
                    'start_time': '7:00pm'
                },
            'place':
                {
                    'place_id': '1',
                    'name': 'Barcadia',
                    'latitude': 32.81169,
                    'longitude': -96.775201,
                    'price': 2,
                    'rating': 4.5,
                    'review_count': 327,
                    'phone': '(214) 721-7300',
                    'photos': [
                        'http://127.0.0.1:8000/media/Barcadia_image.png',
                        'http://127.0.0.1:8000/media/Barcadia_image_2.png',
                    ],
                    'category': 'Drinks',
                    'address1': '1917 N Henderson Ave'
                }
        }
    }

date6 = {
    'Date':
        {
            'date_id': '6',
            'target_likes': True,
            'primary_user_likes': 'undecided',
            'User':
                {
                    'user_id': '2',
                    'name': 'Anthony',
                    'age': '28',
                    'occupation': 'Actor',
                    'education': 'University of North Texas',
                    'about': 'I\'m a kind and sweet gentleman. Everything I do is motivated by the desire to help other people. I\'m an actor and I love my craft. Everytime I go outside I think to myself, "Today is a day to be different. Today is a day to be great." I\'m from Dallas to NYC. Ever since I was born I knew I would be a great person. My mom taught me the power of belief. Now I know this is my super power.',
                    'main_picture': 'http://127.0.0.1:8000/media/Anthony_image.png',
                    'additional_pictures': [
                        'http://127.0.0.1:8000/media/Anthony_image_2.png',
                    ],
                    'mutual_friends': [
                        {'friend':
                             {
                                 'name': 'Matthew',
                                 'picture': 'http://127.0.0.1:8000/media/60x60_matthew.png'
                             }
                         }
                    ]
                },
            'time':
                {
                    'day': 'Sun',
                    'start_time': '11:00am'
                },
            'place':
                {
                    'place_id': '2',
                    'name': 'White Rock Lake',
                    'latitude': 32.828066,
                    'longitude': -96.725316,
                    'price': 0,
                    'rating': 4.5,
                    'review_count': 199,
                    'phone': None,
                    'photos': [
                        'http://127.0.0.1:8000/media/White_rock_lake_image.png',
                        'http://127.0.0.1:8000/media/White_rock_lake_image_2.png',
                    ],
                    'category': 'Nature',
                    'address1': None
                }
        }
    }


now = datetime.now()
respond_by = datetime(now.year, now.month, now.day, now.hour + 12, now.minute, now.second)
date7 = {
    'Date':
        {
            'date_id': '7',
            'target_likes': False,
            'primary_user_likes': 'likes',
            'respond_by': respond_by,
            'User':
                {
                    'user_id': '1',
                    'name': 'Matthew',
                    'age': '27',
                    'occupation': 'World Traveler',
                    'education': 'Yale University',
                    'about': 'I\'m trying to be clever.',
                    'main_picture': 'http://127.0.0.1:8000/media/Matthew_image.png',
                    'additional_pictures': [
                        'http://127.0.0.1:8000/media/Matthew_image_2.png',
                        'http://127.0.0.1:8000/media/Matthew_image_3.png'
                    ],
                    'mutual_friends': [
                        {'friend':
                             {
                                 'name': 'Anthony',
                                 'picture': 'http://127.0.0.1:8000/media/60x60_anthony.png'
                             }
                         }
                    ]
                },
            'time':
                {
                    'day': 'Mon',
                    'start_time': '3:00pm'
                },
            'place':
                {
                    'place_id': '1',
                    'name': 'Barcadia',
                    'latitude': 32.81169,
                    'longitude': -96.775201,
                    'price': 2,
                    'rating': 4.5,
                    'review_count': 327,
                    'phone': '(214) 721-7300',
                    'photos': [
                        'http://127.0.0.1:8000/media/Barcadia_image.png',
                        'http://127.0.0.1:8000/media/Barcadia_image_2.png',
                    ],
                    'category': 'Drinks',
                    'address1': '1917 N Henderson Ave'
                }
        }
    }