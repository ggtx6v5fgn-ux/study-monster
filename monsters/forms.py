from django import forms
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Monster, BattleLog

User = get_user_model()

class MonsterForm(forms.ModelForm):
    """Форма для создания и редактирования монстра"""

    class Meta:
        model = Monster
        fields = ['name', 'description', 'hp', 'difficulty', 'monster_type', 'deadline']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'hp': forms.NumberInput(attrs={'class': 'form-control'}),
            'difficulty': forms.Select(attrs={'class': 'form-control'}),
            'monster_type': forms.Select(attrs={'class': 'form-control'}),
            'deadline': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }

    def clean_name(self):
        """Проверка имени монстра"""
        name = self.cleaned_data.get('name')
        if len(name) < 3:
            raise forms.ValidationError('Имя монстра слишком короткое (минимум 3 символа)')
        return name

    def clean_hp(self):
        """Проверка здоровья монстра"""
        hp = self.cleaned_data.get('hp')
        if hp <= 0:
            raise forms.ValidationError('HP должно быть положительным числом')
        if hp > 1000:
            raise forms.ValidationError('HP не может быть больше 1000')
        return hp

    def clean_deadline(self):
        """Проверка срока выполнения"""
        deadline = self.cleaned_data.get('deadline')
        if deadline and deadline < timezone.now():
            raise forms.ValidationError('Дедлайн не может быть в прошлом')
        return deadline

class BattleLogForm(forms.ModelForm):
    """Форма для атаки на монстра"""

    def __init__(self, *args, **kwargs):
        self.monster = kwargs.pop('monster', None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = BattleLog
        fields = ['damage']
        widgets = {
            'damage': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 100}),
        }

    def clean_damage(self):
        """Проверка урона"""
        damage = self.cleaned_data.get('damage')

        if damage <= 0:
            raise forms.ValidationError('Урон должен быть положительным')
        if damage > 100:
            raise forms.ValidationError('Нельзя нанести более 100 урона за раз')

        if self.monster and damage > self.monster.hp:
            raise forms.ValidationError(
                f'Урон не может превышать оставшееся здоровье монстра ({self.monster.hp} HP)'
            )

        return damage

class UserRegisterForm(UserCreationForm):
    """Форма регистрации пользователя"""

    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].label = 'Пароль'
        self.fields['password2'].label = 'Подтверждение пароля'

