from celery import shared_task
import time

from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string

import datetime as DT
from datetime import timedelta, date

from datetime import datetime, timezone

from .models import Article, UserProfile, User


@shared_task
def subscribe_confirmation_message(user_name, email):
    ''' Email confirmation for weekly newsletter and post digest '''
    send_mail(
        subject=f'Game`s articles Board!: news subscription.',
        message=f'Привет, {user_name}! Спасибо, вы подписались на еженедельный дайджест нашего сайта.',
        from_email='poch7a.7@yandex.ru',
        recipient_list=[f'{email}', ],
    )


@shared_task
def weekly_digest():
    ''' Weekly newsletter and post digest email sending '''
    week = timedelta(days=7)

    subscribers = User.objects.filter(userprofile__news_susbscribed=True)
    subscribers_emails = []
    for subscriber in subscribers:
        subscribers_emails.append(subscriber.email)

    posts = Article.objects.all()
    weekly_posts = []
    now = datetime.now(timezone.utc)

    for article in posts:
        time_delta = now - article.post_date
        if time_delta < week:
            weekly_posts.append(article)

    if subscribers_emails:
        msg = EmailMultiAlternatives(
            subject=f'Weekly news from Game`s articles Board!',
            body=f'Привет! Еженедельная подборка публикаций',
            from_email='poch7a.7@yandex.ru',
            to=subscribers_emails,
        )


        html_content = render_to_string(
            'weekly_digest.html',
            {
                'digest': weekly_posts,
            }
        )

        msg.attach_alternative(html_content, "text/html")

        msg.send()

