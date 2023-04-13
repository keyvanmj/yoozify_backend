import datetime
from django.conf import settings
import pyotp
from kavenegar import KavenegarAPI
from rest_framework.response import Response
from rest_framework.reverse import reverse
from Accounts.signals import is_unique


def generate_key():
    """ User otp key generator """
    key = pyotp.random_base32()
    if is_unique(key):
        return key
    generate_key()

def send_otp(phone):
    if phone:
        key = generate_key()
        time_otp = pyotp.TOTP(key, interval=300)
        time_otp = time_otp.now()

        return time_otp
    else:
        return False


def send_sms_code(*args,**kwargs):
    user_phone_number = kwargs.get('phone')
    otp = kwargs.get('otp')
    message = kwargs.get('message')
    api = KavenegarAPI(settings.KAVEH_NEGAR_API_KEY)
    params = {
        'sender': '10008663',
        'receptor': user_phone_number,
        'message': message
    }
    response = api.sms_send(params)
    data = {
        'verify_phone':reverse('validate_otp'),
    }
    return Response(status=200,data=data)


def send_after_seconds(sec,old_time):
    now = datetime.datetime.now()
    send = False
    if now.timestamp() - old_time.timestamp() > sec:
        send = True
    return send
