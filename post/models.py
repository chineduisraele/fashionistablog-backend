from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User

# Create your models here.


class Post(models.Model):

    @admin.display(
        description='total_comments')
    def get_total_comments(self):
        return len(self.comments.all())
    # upload paths

    def get_image_upload_path(self, filename):
        return f'post_images/{filename}'

    # category choices
    CATEGORIES = (("design", 'Design'), ("fashion", 'Fashion'),
                  ("lifestyle", 'Lifestyle'), ("talks", 'Talks'))

    total_comments = get_total_comments

    # banner image
    image = models.ImageField(
        upload_to=get_image_upload_path)

    category = models.CharField(choices=CATEGORIES, max_length=25)
    featured = models.BooleanField(default=False)
    title = models.CharField(max_length=250)

    # info
    date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(to=User, on_delete=models.CASCADE)
    views = models.PositiveIntegerField(default=0)

    # tags
    tags = models.CharField(max_length=250)

    def __str__(self) -> str:
        return f'{self.date} {self.title[:50]}'

    # instance methods
    def get_author(self):
        return f"{self.author.first_name} {self.author.last_name}"

    def get_paragraphs(self):
        return Paragraph.objects.filter(post=self)

    def get_short_text(self):
        return (Paragraph.objects.filter(post=self))[0].get_short_text()

    # instance method actions

    def update_views(self):
        self.views += 1
        self.save()

    def create_comment(self, name, comment):
        Comment(post=self,
                name=name,
                comment=comment).save()

    # meta

    class Meta:
        ordering = ["-id"]

# paragraph


class Paragraph(models.Model):
    def get_image_upload_path(self, filename):
        return f'posts/post_{self.post.id}/{filename}'

    post = models.ForeignKey(
        to=Post, on_delete=models.CASCADE, related_name="paragraphs")
    image = models.ImageField(
        upload_to=get_image_upload_path, blank=True)
    text = models.TextField()

    # instance methods
    def get_short_text(self):
        return " ".join(self.text.split(" ")[:17])


class Comment(models.Model):
    post = models.ForeignKey(
        to=Post, on_delete=models.CASCADE, related_name="comments")
    name = models.CharField(max_length=50)
    comment = models.TextField(max_length=250)
    date = models.DateTimeField(auto_now_add=True)

    # meta
    class Meta:
        ordering = ["-id"]


# newsfeed subscribers
class NewsFeed(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=50, unique=True)

    def __str__(self):
        return self.email
