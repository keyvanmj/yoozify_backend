from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import User, ChangePhone, Profile
import pyotp


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


def generate_key():
    """ User otp key generator """
    key = pyotp.random_base32()
    if is_unique(key):
        return key
    generate_key()

def is_unique(key):
    try:
        User.objects.get(key=key)
    except User.DoesNotExist:
        return True
    return False

@receiver(pre_save, sender=User)
def create_key(sender, instance, **kwargs):
    """This creates the key for users that don't have keys"""
    if not instance.key:
        instance.key = generate_key()

