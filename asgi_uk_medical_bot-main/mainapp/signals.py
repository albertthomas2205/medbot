from celery.signals import task_failure
from django.core.mail import send_mail

@task_failure.connect
def on_task_failure(sender=None, task_id=None, exception=None, **kwargs):
    send_mail(
        subject=f"[Celery Task Failed] {sender.name}",
        message=f"Task ID: {task_id}\nException: {exception}",
        from_email="alerts@yourdomain.com",
        recipient_list=["you@yourdomain.com"],
    )