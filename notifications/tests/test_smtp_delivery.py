from __future__ import annotations

import logging
import os
from unittest import skipUnless, mock

from django.core.mail import EmailMultiAlternatives, get_connection
from django.test import SimpleTestCase, override_settings

from core import email as core_email

logger = logging.getLogger(__name__)


def _env_bool(key: str, default: bool = False) -> bool:
    val = os.environ.get(key)
    if val is None:
        return default
    return str(val).lower() in {"1", "true", "yes"}


def _env_required(key: str) -> str:
    value = os.environ.get(key)
    if not value:
        raise AssertionError(f"Missing required env var for SMTP test: {key}")
    return value


enable_real = _env_bool("ENABLE_REAL_GMAIL_TEST", False)


def _send_email_via_smtp(
    host: str,
    port: int,
    username: str,
    password: str,
    use_tls: bool,
    use_ssl: bool,
    timeout: int,
    from_email: str,
    recipient: str,
    subject: str,
    body: str,
    html_body: str | None = None,
):
    """Send an email over an SMTP connection and return (send_count, noop_code, noop_msg).

    This helper keeps the low-level SMTP interaction in one place so tests are
    easier to read and assertions are made in the test context.
    """
    connection = get_connection(
        backend="django.core.mail.backends.smtp.EmailBackend",
        host=host,
        port=port,
        username=username,
        password=password,
        use_tls=use_tls,
        use_ssl=use_ssl,
        timeout=timeout,
    )
    logger.info("SMTP connecting", extra={"email_host": host, "email_port": port, "user": username, "recipient": recipient})
    connection.open()
    if getattr(connection, "connection", None) is None:
        raise AssertionError("SMTP connection failed to open")

    email = EmailMultiAlternatives(
        subject=subject,
        body=body,
        from_email=from_email,
        to=[recipient],
        connection=connection,
    )
    if html_body:
        email.attach_alternative(html_body, "text/html")

    send_count = email.send(fail_silently=False)
    logger.info("SMTP send attempted", extra={"email_host": host, "email_port": port, "user": username, "recipient": recipient, "send_count": send_count})

    code, msg = connection.connection.noop()
    logger.info("SMTP NOOP response", extra={"email_host": host, "email_port": port, "user": username, "recipient": recipient, "code": code, "msg": msg})

    connection.close()
    logger.info("SMTP connection closed", extra={"email_host": host, "email_port": port, "user": username, "recipient": recipient})
    return send_count, code, msg


@skipUnless(enable_real, "Real Gmail SMTP test disabled; set ENABLE_REAL_GMAIL_TEST=true to run")
@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend",
)
class GmailSmtpDeliveryTests(SimpleTestCase):
    """
    This test sends a real email via Gmail SMTP. It will be skipped unless
    ENABLE_REAL_GMAIL_TEST is set to true in the environment.
    """

    @classmethod
    def setUpClass(cls):  # pragma: no cover - depends on external SMTP
        super().setUpClass()
        cls.email_host = _env_required("EMAIL_HOST")
        cls.email_port = int(_env_required("EMAIL_PORT"))
        cls.email_user = _env_required("EMAIL_HOST_USER")
        cls.email_password = _env_required("EMAIL_HOST_PASSWORD")
        cls.use_tls = _env_bool("EMAIL_USE_TLS", True)
        cls.use_ssl = _env_bool("EMAIL_USE_SSL", False)
        cls.default_from = os.environ.get("DEFAULT_FROM_EMAIL", cls.email_user)
        cls.recipient = os.environ.get("GMAIL_TEST_RECIPIENT", cls.email_user)

    def test_gmail_smtp_real_delivery(self):  # pragma: no cover - external
        log_extra = {
            "email_host": self.email_host,
            "email_port": self.email_port,
            "user": self.email_user,
            "recipient": self.recipient,
        }

        # Force celery delay to execute synchronously
        with mock.patch.object(core_email, "send_email_task") as mocked_task:
            def _sync_send(subject, body, recipient_email, html_body=None):
                send_count, code, msg = _send_email_via_smtp(
                    host=self.email_host,
                    port=self.email_port,
                    username=self.email_user,
                    password=self.email_password,
                    use_tls=self.use_tls,
                    use_ssl=self.use_ssl,
                    timeout=30,
                    from_email=self.default_from,
                    recipient=recipient_email,
                    subject=subject,
                    body=body,
                    html_body=html_body,
                )
                self.assertEqual(send_count, 1, "Email send did not report success")
                self.assertEqual(code, 250, f"Expected 250 from Gmail, got {code}: {msg}")
                return 1

            mocked_task.delay.side_effect = _sync_send

            subject = "Kanban Manager SMTP Integration Test"
            body = "Text body for SMTP integration test."
            html = "<p><strong>HTML</strong> body for SMTP integration test.</p>"

            # Run through helper to exercise Celery delay mocking
            result = core_email.send_email(subject, body, self.recipient, template=None, context=None)
            self.assertEqual(result, 1, "Celery-backed send_email did not return success")

    def test_missing_credentials_fail_fast(self):  # pragma: no cover - external
        with self.assertRaises(AssertionError):
            _env_required("EMAIL_HOST_USER")
        with self.assertRaises(AssertionError):
            _env_required("EMAIL_HOST_PASSWORD")


# Structured logging setup recommendation for running this test manually:
#   ENABLE_REAL_GMAIL_TEST=true EMAIL_HOST=smtp.gmail.com EMAIL_PORT=587 \
#   EMAIL_HOST_USER=... EMAIL_HOST_PASSWORD=... EMAIL_USE_TLS=true \
#   python manage.py test notifications.tests.test_smtp_delivery.GmailSmtpDeliveryTests --verbosity=2
