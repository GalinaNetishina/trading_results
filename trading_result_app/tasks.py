from celery.schedules import crontab
from config import settings
import requests
from celery import Celery
from redis import asyncio as aioredis

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465

redis = aioredis.from_url(
    f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
    encoding="utf8",
    decode_responses=True,
)
celery = Celery(
    "tasks", broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0"
)


celery.conf.beat_schedule = {
    "clear_cache": {
        "task": "tasks.refresh_cash",
        "schedule": crontab(hour=14, minute=11),
    },
    # "email_tick": {
    #     "task": 'tasks.send_email',
    #     "schedule": timedelta(days=1),
    # },
}


@celery.task
async def refresh_cash():
    await redis.flushdb()
    requests.get("http://127.0.0.1:8000/api/clear_cashe")
    # requests.get('http://127.0.0.1:8000/api/last_trading_dates/?count=10')
    # requests.get('http://127.0.0.1:8000/api/get_trading_results/?limit=100&skip=0')
    return True


# @celery.task
# def send_email(username: str='Iam'):
#     email = get_email_template_dashboard(username)
#     with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
#         server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
#         server.send_message(email)


# def get_email_template_dashboard(username: str):
#     email = EmailMessage()
#     email["Subject"] = "log"
#     email["From"] = settings.SMTP_USER
#     email["To"] = settings.SMTP_USER
#     email.set_content(f"<div>Hello, {username}</div><div>Message from celery</div>", subtype="html")
#     return email
