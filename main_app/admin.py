from django.contrib import admin

from main_app.models import Category, Task


# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'user')
    list_filter = ('user',)
    search_fields = ('name',)

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'priority', 'due_date', 'completed')
    list_filter = ('completed', 'priority', 'user', 'category')
    search_fields = ('title', 'description')


