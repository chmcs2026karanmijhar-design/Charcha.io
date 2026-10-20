
from django.contrib import admin
from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "reporter",
        "reported_content",
        "reason",
        "status",
        "created_at",
    )

    list_filter = ("status", "created_at")
    search_fields = (
        "reporter__username",
        "reason",
        "question__title",
        "answer__body",
    )

    list_editable = ("status",)
    readonly_fields = ("created_at",)

    @admin.display(description="Reported content")
    def reported_content(self, obj):
        if obj.question:
            return f"Question: {obj.question.title}"
        if obj.answer:
            return f"Answer: {obj.answer.body[:60]}"
        return "Content unavailable"




from .models import Question, Answer, Comment, Topic, AnswerRequest

admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Comment)
admin.site.register(Topic)
admin.site.register(AnswerRequest)



from django.contrib import admin

