from django.urls import path
from . import views

app_name = "questions"

urlpatterns = [
    path("", views.home, name="home"),
    path("search/", views.search_questions, name="search"),
    path("ask/", views.ask_question, name="ask"),
    path("bookmarks/", views.bookmarks, name="bookmarks"),

    path(
        "question/<int:question_id>/follow/",
        views.toggle_question_follow,
        name="toggle_question_follow",
    ),
    path(
        "question/<int:question_id>/answer/",
        views.post_answer,
        name="answer",
    ),
    path(
        "question/<int:question_id>/bookmark/",
        views.toggle_bookmark,
        name="toggle_bookmark",
    ),
    path(
        "question/<int:question_id>/",
        views.question_detail,
        name="detail",
    ),

    path(
        "answer/<int:answer_id>/comment/",
        views.post_comment,
        name="comment",
    ),
    path(
        "answer/<int:answer_id>/vote/",
        views.vote_answer,
        name="vote",
    ),
    path(
        "edit/<str:content_type>/<int:content_id>/",
        views.edit_content,
        name="edit_content",
    ),
    path(
        "delete/<str:content_type>/<int:content_id>/",
        views.delete_content,
        name="delete_content",
    ),

    path("topics/", views.topics_list, name="topics"),
    path(
        "topics/<slug:slug>/follow/",
        views.toggle_topic_follow,
        name="toggle_topic_follow",
    ),
    path(
        "topics/<slug:slug>/",
        views.topic_detail,
        name="topic_detail",
    ),
    path("following/", views.following_feed, name="following"),
    path(
    "question/<int:question_id>/request-answer/",
    views.request_answer,
    name="request_answer",
),

path("users/search/", views.search_users, name="search_users"),
path(
    "report/<str:content_type>/<int:content_id>/",
    views.report_content,
    name="report_content",
),

]

