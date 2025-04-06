# Existing configuration settings
MAX_CONTENT_LENGTH = 100 * 1024 * 1024 
DATABASE = 'instance/lexloop.sqlite'
UPLOADS = 'instance/uploads'

# Mail settings
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = 'xxxxxxx@gmail.com'
MAIL_PASSWORD = 'xxxx xxxx xxxx xxxx'
MAIL_DEFAULT_SENDER = ('LexLoop', 'xxxxxxx@gmail.com')

# Security settings for tokens
SECRET_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'