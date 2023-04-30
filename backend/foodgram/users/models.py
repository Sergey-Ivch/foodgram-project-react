from django.db import models
from django.contrib.auth.models import AbstractUser


class Buyer(AbstractUser):
    email = models.EmailField(max_length=254, unique=True)

    def __str__(self):
        return self.username


class Signer(models.Model):
    class Meta:
        verbose_name = 'Подписка на авторов'
        verbose_name_plural = 'Подписки на авторов'
        unique_together = ('user', 'author') 

    user = models.ForeignKey(Buyer,
        on_delete=models.CASCADE, related_name='subscriber')
    author = models.ForeignKey(Buyer,
        on_delete=models.CASCADE, related_name='subscribing')

    def __str__(self):
        return f"{self.user.username}{self.author.username}"

