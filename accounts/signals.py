from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import User, UserProfile



# PostSave Signals
@receiver(post_save, sender=User)
def post_save_create_profile_reciver(sender, instance, created, **kwargs):
    print(created)
    if created:
        UserProfile.objects.create(user=instance)

    else:
        try:
            profile = UserProfile.objects.get(user=instance)
            profile.save()
        
        except:
            UserProfile.objects.create(user=instance)
            print("Profile was not exist but I've created one")



@receiver(pre_save, sender=User)
def pre_save_profile_reciver(sender, instance, **kwargs):
    pass
# post_save.connect(post_save_create_profile_reciver, User)