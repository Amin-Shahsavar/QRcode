from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


class EmailHandler:
    def __init__(self, request, user, *args, **kwargs):
        self.user = user
        self.current_site = get_current_site(request)
        self.uid = urlsafe_base64_encode(force_bytes(user.id))
        self.token = default_token_generator.make_token(user)
        self.from_email = settings.EMAIL_HOST_USER
        self.to_email = [user.email]
    
    def get_email_subject(self, email_type):
        if email_type == 'reset_password':
            return "Reset yout password with this link !"
        return "Verfiy your email with this link !"
    
    def get_email_message(self, email_type):
        if email_type == 'reset_password':
            return f"Click on this link to reset your password {self.current_site}/users/reset_password/{self.uid}/{self.token}/"
        return f"Click on this link to verify your email {self.current_site}/users/verify_email/{self.uid}/{self.token}/"
    
    def send_email(self, email_type):
        subject = self.get_email_subject(email_type)
        message = self.get_email_message(email_type)
        send_mail(subject=subject, message=message, from_email=self.from_email, recipient_list=self.to_email)