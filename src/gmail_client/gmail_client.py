import logging
from email.message import EmailMessage
from email.utils import formatdate

import aiosmtplib

from .errors import NotConnectedError

logger = logging.getLogger(__name__)


class GmailClient:
    def __init__(self, email: str, password: str) -> None:
        self.email = email
        self.password = password
        self.hostname = "smtp.gmail.com"

    async def __aenter__(self):
        self._connection = aiosmtplib.SMTP(
            hostname=self.hostname,
            port=587,
            username=self.email,
            password=self.password,
            start_tls=True,
        )
        await self._connection.connect()
        await self._connection.login(self.email, self.password)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._connection.quit()

    def _ensure_connected(self):
        if getattr(self, "_smtp", None) is None:
            raise NotConnectedError(
                "SMTP connection not established. Use 'async with GmailClient(...)'."
            )

    async def send_email(
        self,
        subject: str,
        receiver_address: str,
        html_content: str,
    ):
        self._ensure_connected()

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = self.email
        msg["To"] = receiver_address
        msg["Date"] = formatdate(localtime=True)

        html = (
            """
        <html>
            <body>     
        """
            + html_content
            + """
            </body>
        </html>
        """
        )

        msg.add_alternative(html, subtype="html")

        # Send the message via our own SMTP server.
        await self._connection.send_message(msg)

        logger.info("Mail sent successfully")

        return True
