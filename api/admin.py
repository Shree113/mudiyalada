from django.contrib import admin
from .models import Student, Question, StudentAnswer, Leaderboard

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'department', 'college', 'year', 'total_score', 'needs_retest')
    search_fields = ('name', 'email', 'department')
    list_filter = ('department', 'year', 'needs_retest')
    actions = ['mark_for_retest', 'unmark_retest']

    def mark_for_retest(self, request, queryset):
        queryset.update(needs_retest=True)
    mark_for_retest.short_description = "Mark selected students for retest"

    def unmark_retest(self, request, queryset):
        queryset.update(needs_retest=False)
    unmark_retest.short_description = "Remove retest mark from selected students"

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option', 'is_retest')
    search_fields = ('text',)
    list_filter = ('is_retest',)  # Add filter for retest questions
    fieldsets = (
        ('Question', {
            'fields': ('text', 'is_retest')
        }),
        ('Options', {
            'fields': ('option_a', 'option_b', 'option_c', 'option_d', 'correct_option')
        }),
    )

@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ('student', 'question', 'chosen_option', 'is_correct')
    list_filter = ('is_correct',)

@admin.register(Leaderboard)
class LeaderboardAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'department', 'total_score')
    ordering = ('-total_score',)
    list_filter = ('department', 'year')
    search_fields = ('name', 'email')
    readonly_fields = ('total_score',)
