import os



if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/'):
    app_url = 'https://onlinebookform.appspot.com/'
else:
    app_url = 'http://localhost:8080'