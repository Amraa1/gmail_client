from email.message import EmailMessage
from email.utils import formatdate

import aiosmtplib

from core.logging import MAIL_LOGGER


class GmailClient:
    def __init__(self, email: str, password: str) -> None:
        self.EMAIL = email
        self.PASSWORD = password

    async def send_email(
        self,
        subject: str,
        receiver_address: str,
        html_content: str,
    ):
        self.msg = EmailMessage()
        self.msg["Subject"] = subject
        self.msg["From"] = self.EMAIL
        self.msg["To"] = receiver_address
        self.msg["Date"] = formatdate(localtime=True)

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

        self.msg.add_alternative(html, subtype="html")

        # Send the message via our own SMTP server.
        s = aiosmtplib.SMTP(
            hostname="smtp.gmail.com",
            port=587,
            username=self.EMAIL,
            password=self.PASSWORD,
            start_tls=True,
        )
        await s.connect()
        await s.send_message(self.msg)
        await s.quit()

        MAIL_LOGGER.info("Mail sent successfully")

        return True
