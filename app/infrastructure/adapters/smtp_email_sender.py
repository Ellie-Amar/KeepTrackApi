from __future__ import annotations

import asyncio
import smtplib
from email.message import EmailMessage

from app.application.ports.email_sender import IEmailSender


class SmtpEmailSender(IEmailSender):
    def __init__(
        self,
        *,
        host: str,
        port: int,
        username: str,
        password: str,
        sender_email: str,
        sender_name: str = "KeepTrack",
    ) -> None:
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._sender_email = sender_email
        self._sender_name = sender_name

    async def send(
        self,
        *,
        to_email: str,
        subject: str,
        text_body: str,
        html_body: str | None = None,
    ) -> None:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = f"{self._sender_name} <{self._sender_email}>"
        msg["To"] = to_email
        msg.set_content(text_body)
        if html_body:
            msg.add_alternative(html_body, subtype="html")
        await asyncio.to_thread(self._send_sync, msg)

    def _send_sync(self, msg: EmailMessage) -> None:
        with smtplib.SMTP(self._host, self._port, timeout=20) as smtp:
            smtp.starttls()
            smtp.login(self._username, self._password)
            smtp.send_message(msg)


class NoopEmailSender(IEmailSender):
    async def send(
        self,
        *,
        to_email: str,
        subject: str,
        text_body: str,
        html_body: str | None = None,
    ) -> None:
        return None
