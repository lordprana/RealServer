from django.utils import timezone
from datetime import datetime, timedelta

respond_by = timezone.now() + timedelta(hours=24)
dates = {}
dates['sun'] = {
    'date':
        {
            'date_id': '1',
            'potential_date_likes': False,
            'primary_user_likes': 'undecided',
            'respond_by': respond_by.isoformat(),
            'match':
                {
                    'user_id': '1',
                    'name': 'Maksym',
                    'age': '27',
                    'occupation': 'World Traveler',
                    'education': 'Yale University',
                    'about': 'I\'m trying to be clever.',
                    'main_picture': 'https://realdatingbucket.s3.amazonaws.com/1829561367333153/sqbtyajqlhpb',
                    'detail_pictures': [
                        'https://realdatingbucket.s3.amazonaws.com/1829561367333153/bvdtjxvqfhdo'
                        'https://realdatingbucket.s3.amazonaws.com/1829561367333153/fhjkoiqciraw',
                    ],
                    'mutual_friends': [
                        {'friend':
                             {
                                 'name': 'Matthew',
                                 'picture': 'https://realdatingbucket.s3.amazonaws.com/2959531196950/rgifzhzprsmn'
                             }
                         }
                    ]
                },
            'time':
                {
                    'day': 'sun',
                    'start_time': '7:00pm'
                },
            'place':
                {
                    'place_id': 'barcadia-dallas',
                }
        }
    }

dates['mon'] = {
    'date':
        {
            'date_id': '2',
            'potential_date_likes': True,
            'primary_user_likes': 'undecided',
            'respond_by': respond_by.isoformat(),
            'match':
                {
                    'user_id': '1',
                    'name': 'Maksym',
                    'age': '27',
                    'occupation': 'World Traveler',
                    'education': 'Yale University',
                    'about': 'I\'m trying to be clever.',
                    'main_picture': 'https://realdatingbucket.s3.amazonaws.com/1829561367333153/sqbtyajqlhpb',
                    'detail_pictures': [
                        'https://realdatingbucket.s3.amazonaws.com/1829561367333153/bvdtjxvqfhdo'
                        'https://realdatingbucket.s3.amazonaws.com/1829561367333153/fhjkoiqciraw',
                    ],
                    'mutual_friends': [
                        {'friend':
                             {
                                 'name': 'Matthew',
                                 'picture': 'https://realdatingbucket.s3.amazonaws.com/2959531196950/rgifzhzprsmn'
                             }
                         }
                    ]
                },
            'time':
                {
                    'day': 'mon',
                    'start_time': '9:00pm'
                },
            'place':
                {
                    'place_id': 'barcadia-dallas',
                }
        }
    }

dates['tue'] = {
    'date':
        {
            'date_id': '3',
            'potential_date_likes': False,
            'primary_user_likes': 'pass',
            'respond_by': respond_by.isoformat(),
            'match':
                {
                    'user_id': '1',
                    'name': 'Maksym',
                    'age': '27',
                    'occupation': 'World Traveler',
                    'education': 'Yale University',
                    'about': 'I\'m trying to be clever.',
                    'main_picture': 'https://realdatingbucket.s3.amazonaws.com/1829561367333153/sqbtyajqlhpb',
                    'detail_pictures': [
                        'https://realdatingbucket.s3.amazonaws.com/1829561367333153/bvdtjxvqfhdo'
                        'https://realdatingbucket.s3.amazonaws.com/1829561367333153/fhjkoiqciraw',
                    ],
                    'mutual_friends': [
                        {'friend':
                             {
                                 'name': 'Matthew',
                                 'picture': 'https://realdatingbucket.s3.amazonaws.com/2959531196950/rgifzhzprsmn'
                             }
                         }
                    ]
                },
            'time':
                {
                    'day': 'tue',
                    'start_time': '10:00pm'
                },
            'place':
                {
                    'place_id': 'barcadia-dallas',
                }
        }
    }

dates['wed'] = {
    'date':
        {
            'date_id': '4',
            'potential_date_likes': False,
            'primary_user_likes': 'undecided',
            'respond_by': respond_by.isoformat(),
            'match':
                {
                    'user_id': '1',
                    'name': 'Maksym',
                    'age': '27',
                    'occupation': 'World Traveler',
                    'education': 'Yale University',
                    'about': 'I\'m trying to be clever.',
                    'main_picture': 'https://realdatingbucket.s3.amazonaws.com/1829561367333153/sqbtyajqlhpb',
                    'detail_pictures': [
                        'https://realdatingbucket.s3.amazonaws.com/1829561367333153/bvdtjxvqfhdo'
                        'https://realdatingbucket.s3.amazonaws.com/1829561367333153/fhjkoiqciraw',
                    ],
                    'mutual_friends': [
                        {'friend':
                             {
                                 'name': 'Matthew',
                                 'picture': 'https://realdatingbucket.s3.amazonaws.com/2959531196950/rgifzhzprsmn'
                             }
                         }
                    ]
                },
            'time':
                {
                    'day': 'wed',
                    'start_time': '12:00pm'
                },
            'place':
                {
                    'place_id': 'barcadia-dallas',
                }
        }
    }

dates['thur'] = {
    'date':
        {
            'date_id': '5',
            'potential_date_likes': False,
            'primary_user_likes': 'undecided',
            'respond_by': respond_by.isoformat(),
            'match':
                {
                    'user_id': '1',
                    'name': 'Maksym',
                    'age': '27',
                    'occupation': 'World Traveler',
                    'education': 'Yale University',
                    'about': 'I\'m trying to be clever.',
                    'main_picture': 'https://realdatingbucket.s3.amazonaws.com/1829561367333153/sqbtyajqlhpb',
                    'detail_pictures': [
                        'https://realdatingbucket.s3.amazonaws.com/1829561367333153/bvdtjxvqfhdo'
                        'https://realdatingbucket.s3.amazonaws.com/1829561367333153/fhjkoiqciraw',
                    ],
                    'mutual_friends': [
                        {'friend':
                             {
                                 'name': 'Matthew',
                                 'picture': 'https://realdatingbucket.s3.amazonaws.com/2959531196950/rgifzhzprsmn'
                             }
                         }
                    ]
                },
            'time':
                {
                    'day': 'thur',
                    'start_time': '2:00pm'
                },
            'place':
                {
                    'place_id': 'barcadia-dallas',
                }
        }
    }

dates['fri'] = {
    'date':
        {
            'date_id': '6',
            'potential_date_likes': True,
            'primary_user_likes': 'likes',
            'last_sent_message': 'OMG I\'m so excited for our date!',
            'respond_by': respond_by.isoformat(),
            'match':
                {
                    'user_id': '1',
                    'name': 'Maksym',
                    'age': '27',
                    'occupation': 'World Traveler',
                    'education': 'Yale University',
                    'about': 'I\'m trying to be clever.',
                    'main_picture': 'https://realdatingbucket.s3.amazonaws.com/1829561367333153/sqbtyajqlhpb',
                    'detail_pictures': [
                        'https://realdatingbucket.s3.amazonaws.com/1829561367333153/bvdtjxvqfhdo'
                        'https://realdatingbucket.s3.amazonaws.com/1829561367333153/fhjkoiqciraw',
                    ],
                    'mutual_friends': [
                        {'friend':
                             {
                                 'name': 'Matthew',
                                 'picture': 'https://realdatingbucket.s3.amazonaws.com/2959531196950/rgifzhzprsmn'
                             }
                         }
                    ]
                },
            'time':
                {
                    'day': 'fri',
                    'start_time': '2:00pm'
                },
            'place':
                {
                    'place_id': 'white-rock-lake-dallas',
                }
        }
    }

dates['sat'] = {
    'date':
        {
            'date_id': '7',
            'potential_date_likes': False,
            'primary_user_likes': 'likes',
            'respond_by': respond_by.isoformat(),
            'match':
                {
                    'user_id': '1',
                    'name': 'Maksym',
                    'age': '27',
                    'occupation': 'World Traveler',
                    'education': 'Yale University',
                    'about': 'I\'m trying to be clever.',
                    'main_picture': 'https://realdatingbucket.s3.amazonaws.com/1829561367333153/sqbtyajqlhpb',
                    'detail_pictures': [
                        'https://realdatingbucket.s3.amazonaws.com/1829561367333153/bvdtjxvqfhdo'
                        'https://realdatingbucket.s3.amazonaws.com/1829561367333153/fhjkoiqciraw',
                    ],
                    'mutual_friends': [
                        {'friend':
                             {
                                 'name': 'Matthew',
                                 'picture': 'https://realdatingbucket.s3.amazonaws.com/2959531196950/rgifzhzprsmn'
                             }
                         }
                    ]
                },
            'time':
                {
                    'day': 'sat',
                    'start_time': '2:00pm'
                },
            'place':
                {
                    'place_id': 'white-rock-lake-dallas',
                }
        }
    }