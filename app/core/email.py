import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.FROM_EMAIL
        self.app_name = settings.APP_NAME

    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> bool:
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.app_name} <{self.from_email}>"
            msg["To"] = to_email

            text_part = MIMEText(body, "plain")
            msg.attach(text_part)

            if html_body:
                html_part = MIMEText(html_body, "html")
                msg.attach(html_part)

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

    def send_verification_email(self, to_email: str, token: str) -> bool:
        verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
        
        subject = f"Verify your email for {self.app_name}"
        
        body = f"""
Hello,

Please verify your email address by clicking the link below:

{verification_url}

This link will expire in 24 hours.

If you didn't create an account with us, please ignore this email.

Best regards,
{self.app_name} Team
        """
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .button {{ display: inline-block; padding: 12px 24px; background-color: #007bff; color: white; text-decoration: none; border-radius: 4px; }}
        .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; font-size: 0.9em; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>Verify Your Email</h2>
        <p>Hello,</p>
        <p>Please verify your email address by clicking the button below:</p>
        <p style="margin: 30px 0;">
            <a href="{verification_url}" class="button">Verify Email</a>
        </p>
        <p>Or copy and paste this link into your browser:</p>
        <p style="word-break: break-all; color: #007bff;">{verification_url}</p>
        <p>This link will expire in 24 hours.</p>
        <div class="footer">
            <p>If you didn't create an account with us, please ignore this email.</p>
            <p>Best regards,<br>{self.app_name} Team</p>
        </div>
    </div>
</body>
</html>
        """
        
        return self.send_email(to_email, subject, body, html_body)

    def send_password_reset_email(self, to_email: str, token: str) -> bool:
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
        
        subject = f"Password Reset for {self.app_name}"
        
        body = f"""
Hello,

You requested a password reset. Click the link below to reset your password:

{reset_url}

This link will expire in 1 hour.

If you didn't request this, please ignore this email.

Best regards,
{self.app_name} Team
        """
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .button {{ display: inline-block; padding: 12px 24px; background-color: #dc3545; color: white; text-decoration: none; border-radius: 4px; }}
        .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; font-size: 0.9em; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>Password Reset Request</h2>
        <p>Hello,</p>
        <p>You requested a password reset. Click the button below to reset your password:</p>
        <p style="margin: 30px 0;">
            <a href="{reset_url}" class="button">Reset Password</a>
        </p>
        <p>Or copy and paste this link into your browser:</p>
        <p style="word-break: break-all; color: #dc3545;">{reset_url}</p>
        <p>This link will expire in 1 hour.</p>
        <div class="footer">
            <p>If you didn't request this, please ignore this email and your password will remain unchanged.</p>
            <p>Best regards,<br>{self.app_name} Team</p>
        </div>
    </div>
</body>
</html>
        """
        
        return self.send_email(to_email, subject, body, html_body)


email_service = EmailService()