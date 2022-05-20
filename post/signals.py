from django.db.models.signals import post_save
from django.dispatch import receiver

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from app.settings import EMAIL_HOST_USER

from .models import Post, NewsFeed

# send mail


def sendMail(sender, receiver, subject, template, context=None):
    html_message = render_to_string(
        template, context)

    plain_message = strip_tags(html_message)

    send_mail(subject, plain_message, sender,
              receiver, html_message=html_message)


# signals
# new subscriber notif
@receiver(post_save, sender=NewsFeed)
def send_new_subscriber_email(sender, instance, created, **kwargs):
    if created:
        context = {
            'name': instance.name,
        }

        sendMail(EMAIL_HOST_USER, [instance.email],
                 "Welcome to Fashionista", "email/welcome_subscriber.html", context
                 )


# new post notif
@receiver(post_save, sender=Post)
def send_newsfeed_email(sender, instance, created, **kwargs):
    if created:
        # print(Paragraph.objects.filter(post=instance)[0])
        pass
    # subject = f'Fashionista  - Added a new post in {instance.get_category_display()}'
    # context = {
    #     'title': instance.title,
    #     'shorttext': instance.get_short_text()
    # }
    # receivers = [instance.email for instance in NewsFeed.objects.all()]

    # for receiver in receivers:
    #     sendMail(EMAIL_HOST_USER, [receiver], subject,
    #              "email/new_post.html", context)
