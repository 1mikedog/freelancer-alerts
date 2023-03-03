# Freelancer Alerts
Get discord alerts from freelancer.com about new jobs  matching your skills\
Create a postresql db on heroku and run this with scheduler every 10 minutes

Create a config.py file that looks like this and fill out the information OR set config vars on Heroku
```python
DATABASE_URL = ""
WEBHOOK = ""
JOBS = [ '13', '95', '1075' ]
PINGROLE = "<@&1081006453831241798>"
```
