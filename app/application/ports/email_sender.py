from __future__ import annotations

from typing import Protocol


class IEmailSender(Protocol):
    async def send(
        self,
        *,
        to_email: str,
        subject: str,
        text_body: str,
        html_body: str | None = None,
    ) -> None: ...
