from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.auth.models import User

from .models import Comment, UserProfile


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    ''' Signal to automatically create a UserProfile for new users who register on the platform '''
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=Comment)
def comment_notify(sender, instance, created, **kwargs): 
    ''' Signal to notify the author of a comment about a change in the status of his comment '''
    if instance.approved_comment:
        subject = f'{instance.author}, Ваш отзыв принят!!!'
        body = f'Dear {instance.author}, Ваш отзыв от {instance.date_added.strftime("%d-%m-%Y")} по объявлению "{instance.post.title}" by {instance.post.author} принят ...'
        email = instance.author.email

    if not instance.approved_comment:
        subject = f'{instance.author}, Ваш отзыв отклонен...'
        body = f'Dear {instance.author}, Ваш отзыв от {instance.date_added.strftime("%d-%m-%Y")} по объявлению "{instance.post.title}" by {instance.post.author} отклонен ...'
        email = instance.author.email

    if created:
        subject = f'Dear {instance.post.author}, новый отзыв {instance.author} по объявлению "{instance.post.title}" ...'
        body = f'Dear {instance.post.author}, Вы получили новый отзыв по объявлению "{instance.post.title}" от {instance.author} на {instance.date_added.strftime("%d-%m-%Y %H:%M")} ...'
        email = instance.post.author.email

    msg = EmailMultiAlternatives(
        subject=subject,
        body=body,
        from_email='poch7a.7@yandex.ru',
        to=[email]
    )

    html_content = render_to_string(
        'comment_created.html',
        {
            'comment': instance,
            'body': body
        }
    )

    msg.attach_alternative(html_content, "text/html")

    msg.send()


@receiver(post_delete, sender=Comment)
def delete_comment_notify(sender, instance, **kwargs): 
    ''' signal to notify the author of a comment about the deletion of his comment '''
    subject = f'{instance.author}, Ваш отзыв удален...'
    body = f'Привет, {instance.author}! Ваш отзыв от  {instance.date_added.strftime("%d-%m-%Y")} по объявлению "{instance.post.title}" автора {instance.post.author} был удален ...'
    email = instance.author.email

    msg = EmailMultiAlternatives(
        subject=subject,
        body=body,
        from_email='poch7a.7@yandex.ru',
        to=[email]
    )

    html_content = render_to_string(
        'comment_created.html',
        {
            'comment': instance,
            'body': body
        }
    )

    msg.attach_alternative(html_content, "text/html")

    msg.send()


@receiver(post_save, sender=User)
def profile_notify(sender, instance, created, **kwargs):
    ''' Signal to notify the user about changes of his profile settings '''
    subject = f'Привет, {instance.username}! Ваш профиль на сайте Game`s articles Board! изменен!'
    body = f'Привет, {instance.username}! Ваш профиль на сайте Game`s articles Board! был изменен!'
    email = instance.email

    msg = EmailMultiAlternatives(
        subject=subject,
        body=body,
        from_email='poch7a.7@yandex.ru',
        to=[email]
    )

    html_content = render_to_string(
        'profile_email.html',
        {
            'userprofile': instance.userprofile,
            'body': body
        }
    )

    msg.attach_alternative(html_content, "text/html")

    msg.send()

