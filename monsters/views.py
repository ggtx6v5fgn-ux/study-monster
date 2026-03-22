from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Monster, Profile
from .forms import MonsterForm, BattleLogForm, UserRegisterForm


class MonsterListView(LoginRequiredMixin, ListView):
    """Страница со списком монстров"""
    model = Monster
    template_name = 'monsters/monster_list.html'
    context_object_name = 'monsters'

    def get_queryset(self):
        """Показываем только монстров текущего пользователя"""
        return Monster.objects.filter(owner=self.request.user)

class MonsterDetailView(LoginRequiredMixin, DetailView):
    """Детальная страница монстра"""
    model = Monster
    template_name = 'monsters/monster_detail.html'
    context_object_name = 'monster'

    def get_queryset(self):
        """Проверяем, что монстр принадлежит текущему пользователю"""
        return Monster.objects.filter(owner=self.request.user)

class MonsterCreateView(LoginRequiredMixin, CreateView):
    """Создание нового монстра"""
    model = Monster
    form_class = MonsterForm
    template_name = 'monsters/monster_form.html'
    success_url = reverse_lazy('monster_list')

    def form_valid(self, form):
        """Назначаем текущего пользователя владельцем"""
        form.instance.owner = self.request.user
        return super().form_valid(form)

class MonsterUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование монстра"""
    model = Monster
    form_class = MonsterForm
    template_name = 'monsters/monster_form.html'
    success_url = reverse_lazy('monster_list')

    def get_queryset(self):
        """Проверяем, что монстр принадлежит текущему пользователю"""
        return Monster.objects.filter(owner=self.request.user)

class MonsterDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление монстра"""
    model = Monster
    template_name = 'monsters/monster_confirm_delete.html'
    success_url = reverse_lazy('monster_list')

    def get_queryset(self):
        """Проверяем, что монстр принадлежит текущему пользователю"""
        return Monster.objects.filter(owner=self.request.user)

def battle_monster(request, pk):
    """Функция для атаки на монстра"""
    monster = get_object_or_404(Monster, pk=pk, owner=request.user)

    if request.method == 'POST':
        form = BattleLogForm(request.POST, monster=monster)
        if form.is_valid():
            damage = form.cleaned_data['damage']

            # Создаём запись о битве
            battle = form.save(commit=False)
            battle.monster = monster
            battle.user = request.user
            battle.save()

            # Уменьшаем HP монстра
            monster.hp -= damage

            # Проверяем, побеждён ли монстр
            if monster.hp <= 0:
                monster.defeated = True
                monster.defeated_at = timezone.now()
                monster.hp = 0

                # Начисляем опыт игроку
                profile, _ = Profile.objects.get_or_create(user=request.user, defaults={
                    'xp': 0,
                    'level': 1,
                    'monsters_defeated': 0
                })
                xp_reward = monster.difficulty * 50
                profile.add_xp(xp_reward)
                profile.monsters_defeated += 1
                profile.save()

                messages.success(request, f'🎉 Вы победили монстра! +{xp_reward} XP')
            else:
                messages.success(request, f'⚔️ Вы нанесли {damage} урона!')

            monster.save()
            return redirect('monster_detail', pk=monster.pk)
    else:
        form = BattleLogForm(monster=monster)

    return render(request, 'monsters/battle_form.html', {
        'form': form,
        'monster': monster
    })

def register(request):
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Аккаунт создан для {username}! Теперь вы можете войти.')
            return redirect('login')
    else:
        form = UserRegisterForm()

    return render(request, 'registration/register.html', {'form': form})
