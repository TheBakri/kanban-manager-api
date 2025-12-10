from __future__ import annotations

import logging
from typing import Optional

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def send_email_task(self, subject: str, body: str, recipient_email: str, html_body: str | None = None) -> Optional[int]:
    """Send a single email using Django's EmailMessage. Runs in Celery worker."""
    try:
        email = EmailMultiAlternatives(
            subject=subject,
            body=body,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
            to=[recipient_email],
        )
        if html_body:
            email.attach_alternative(html_body, "text/html")
        sent_count = email.send(fail_silently=False)
        log_extra = {"email": recipient_email, "subject": subject}
        if sent_count:
            logger.info("Email sent", extra=log_extra)
        else:
            logger.warning("Email send returned 0", extra=log_extra)
        return sent_count
    except Exception:
        logger.exception("Email send failed", extra={"email": recipient_email, "subject": subject})
        raise


def send_email(subject: str, body: str, recipient_email: str, *, template: str | None = None, context: dict | None = None):
    """Enqueue an email to be sent asynchronously via Celery with optional HTML template."""
    if not recipient_email:
        logger.warning("Skipping email send because recipient is empty", extra={"subject": subject})
        return None

    html_body = None
    if template:
        ctx = {"subject": subject, "body": body, **(context or {})}
        html_body = render_to_string(template, ctx)
    else:
        html_body = render_to_string("emails/base.html", {"subject": subject, "body": body})

    return send_email_task.delay(subject, body, recipient_email, html_body)
