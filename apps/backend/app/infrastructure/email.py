import logging
from abc import ABC, abstractmethod


class EmailProvider(ABC):
    @abstractmethod
    async def send(self, recipient: str, subject: str, body: str) -> None: ...


class DevelopmentEmailProvider(EmailProvider):
    async def send(self, recipient: str, subject: str, body: str) -> None:
        logging.getLogger("app.email").info(
            "development_email", extra={"recipient": recipient, "subject": subject, "body": body}
        )
