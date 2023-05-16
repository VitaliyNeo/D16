from django.contrib import admin
from .models import Article, UserProfile, Comment


admin.site.register(Article)
admin.site.register(UserProfile)
admin.site.register(Comment)
