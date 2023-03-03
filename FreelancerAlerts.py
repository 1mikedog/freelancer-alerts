import requests
import json
from discord_webhook import DiscordWebhook, DiscordEmbed
import time
from google_currency import convert
import pickle
from datetime import datetime
import psycopg2
import pytz
import os
from database import *

try:
    import config
except:
    pass

try:
    DATABASE_URL = os.environ['DATABASE_URL']
except:
    DATABASE_URL = config.DATABASE_URL
try:
    WEBHOOK = os.environ['WEBHOOK']
except:
    WEBHOOK = config.WEBHOOK
try:
    JOBS = os.environ['JOBS'].split(',')
except:
    JOBS = config.JOBS
try:
    PINGROLE = os.environ['PINGROLE']
except:
    PINGROLE = config.PINGROLE

connection = psycopg2.connect(DATABASE_URL, sslmode='require')
db = Database(connection=connection)

params = {
    'limit': '20',
    'full_description': 'true',
    'job_details': 'true',
    'local_details': 'true',
    'location_details': 'true',
    'upgrade_details': 'true',
    'user_country_details': 'true',
    'user_details': 'true',
    'user_employer_reputation': 'true',
    'user_status': 'true',
    'jobs[]': JOBS,
    'languages[]': 'en',
    'sort_field': 'submitdate',
    'webapp': '1',
    'compact': 'true',
    'new_errors': 'true',
    'new_pools': 'true',
}
runs = 1
while True:
    response = requests.get('https://www.freelancer.com/api/projects/0.1/projects/active', params=params)
    json_obj = json.loads(response.text)
    projects = json_obj["result"]["projects"]
    projects.reverse()
    for project in projects:
        title = project["title"]
        url = "https://freelancer.com/projects/" + project["seo_url"] + "/details"
        exists = db.getJob(url)
        if exists:
            continue

        epoch_time = int(project["submitdate"])
        now_time = time.time()

        if now_time - epoch_time > 60 * 60:
            print("OLDER THAN AN HOUR!!")
            db.saveJob(url)
            continue

        jobs_string = []
        for job in project["jobs"]:
            jobs_string.append(job["name"])
        jobs_string = ", ".join(jobs_string)
        description = project["description"]
        currency = project["currency"]["sign"]
        currency_code = project["currency"]["code"]
        try:
            budget_min = int(project["budget"]["minimum"])
        except:
            budget_min = None
        try:
            budget_max = int(project["budget"]["maximum"])
        except:
            budget_max = None

        if currency_code != "USD":
            if budget_min:
                converted1= json.loads(convert(currency_code, "USD", budget_min))
                budget_min = int(float(converted1["amount"]))

            if budget_max:
                converted2= json.loads(convert(currency_code, "USD", budget_max))
                budget_max = int(float(converted2["amount"]))

            currency_code = "USD"
            currency = "$"

        project_type = project["type"]

        utc_dt = datetime.utcfromtimestamp(epoch_time).replace(tzinfo=pytz.utc)
        tz = pytz.timezone('America/Los_Angeles')
        dt = utc_dt.astimezone(tz)

        date = dt.strftime('%Y-%m-%d %I:%M %p')

        webhook = DiscordWebhook(url=WEBHOOK, content=PINGROLE)

        embed = DiscordEmbed(title=title, description=description, url=url)
        embed.set_author(name=jobs_string)
        embed.add_embed_field(name="Type:", value=project_type.upper(), inline=True)
        embed.add_embed_field(name="Currency:", value=currency_code, inline=True)
        if budget_max:
            embed.add_embed_field(name="Budget:", value="{}{}-{}".format(currency, budget_min, budget_max), inline=True)
        else:
            embed.add_embed_field(name="Budget:", value="{}{}+".format(currency, budget_min), inline=True)
        embed.set_footer(text="{}".format(date))
        webhook.add_embed(embed)

        while True:
            try:
                response = webhook.execute()
                print(response.status_code)
            except:
                response = response[0]
                print(response.status_code)
            if response.status_code == 200:
                db.saveJob(url)
                break
            else:
                time.sleep(1)
    runs += 1
    if runs > 9:
        print("BREAKING!!!")
        break
    time.sleep(65)
