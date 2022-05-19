from django.contrib import admin

from .models import Post, Paragraph, Comment, NewsFeed


# create inlines and admins here
class ParagraphInline(admin.StackedInline):
    model = Paragraph
    extra = 0


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'views',
                    'category', 'total_comments')

    inlines = [ParagraphInline, CommentInline]


# Register your models here.
admin.site.register(Post, PostAdmin)

# register newsfeed
admin.site.register(NewsFeed)
