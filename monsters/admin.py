from django.contrib import admin
from .models import Monster, Profile, BattleLog

@admin.register(Monster)
class MonsterAdmin(admin.ModelAdmin):
    list_display = ('name', 'hp', 'difficulty', 'monster_type', 'defeated', 'created_at')
    list_filter = ('difficulty', 'monster_type', 'defeated')
    search_fields = ('name',)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'level', 'xp', 'monsters_defeated')
    search_fields = ('user__username',)

@admin.register(BattleLog)
class BattleLogAdmin(admin.ModelAdmin):
    list_display = ('monster', 'user', 'damage', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('monster__name', 'user__username')
