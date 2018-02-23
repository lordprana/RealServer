# Import smtplib for the actual sending function
import requests


# Open a plain text file for reading.  For this example, assume that
# the text file contains only ASCII characters.
def sendLoggingEmail(subject, message):
    MAILGUN_KEY = os.environ.get('MAILGUN_KEY')
    data = {
        'from': 'Server logging <mailgun@getrealation.com>',
        'to': 'server_logging@getrealation.com',
        'subject': subject,
        'text': message
    }
    r = requests.post('https://api.mailgun.net/v3/mg.getrealation.com/messages', auth=('api', MAILGUN_KEY),
                 data=data)
