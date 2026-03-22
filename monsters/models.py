from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()

class Monster(models.Model):
    """Модель монстра"""
    DIFFICULTY_CHOICES = [
        (1, 'Легкий'),
        (2, 'Средний'),
        (3, 'Сложный'),
    ]

    TYPE_CHOICES = [
        ('fire', '🔥 Огненный'),
        ('water', '💧 Водный'),
        ('earth', '🌍 Земляной'),
        ('air', '💨 Воздушный'),
    ]

    name = models.CharField('Имя', max_length=200)
    description = models.TextField('Описание', blank=True)
    hp = models.IntegerField('Здоровье', default=100)
    difficulty = models.IntegerField('Сложность', choices=DIFFICULTY_CHOICES, default=1)
    monster_type = models.CharField('Тип монстра', max_length=20, choices=TYPE_CHOICES, default='fire')
    deadline = models.DateTimeField('Срок выполнения', null=True, blank=True)
    defeated = models.BooleanField('Побеждён?', default=False)
    defeated_at = models.DateTimeField('Дата победы', null=True, blank=True)
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='monsters',
        verbose_name='Владелец'
    )

    def __str__(self):
        return self.name

    def is_overdue(self):
        """Проверка, просрочен ли монстр"""
        if self.deadline and not self.defeated:
            return self.deadline < timezone.now()
        return False

class Profile(models.Model):
    """Профиль пользователя с игровыми характеристиками"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    xp = models.IntegerField('Опыт', default=0)
    level = models.IntegerField('Уровень', default=1)
    monsters_defeated = models.IntegerField('Побеждено монстров', default=0)

    def __str__(self):
        return f"{self.user.username} - Ур.{self.level} ({self.xp} XP)"

    def add_xp(self, amount):
        """Добавление опыта и повышение уровня"""
        self.xp += amount
        # Повышаем уровень каждые 100 очков опыта
        new_level = self.xp // 100 + 1
        self.level = max(self.level, new_level)
        self.save()

class BattleLog(models.Model):
    """Лог сражения с монстром"""
    monster = models.ForeignKey(Monster, on_delete=models.CASCADE, related_name='battles')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    damage = models.IntegerField('Нанесённый урон')
    created_at = models.DateTimeField('Дата атаки', auto_now_add=True)

    def __str__(self):
        return f"{self.user} атаковал {self.monster} на {self.damage} HP"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Создание профиля при регистрации пользователя"""
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Сохранение профиля"""
    instance.profile.save()
