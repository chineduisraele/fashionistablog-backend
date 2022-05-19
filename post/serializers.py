from rest_framework.serializers import SerializerMethodField, ModelSerializer
from .models import Post, Paragraph, Comment, NewsFeed


class ParagraphSerializer(ModelSerializer):
    class Meta:
        model = Paragraph
        fields = ["id", "image", "text"]


class CommentSerializer(ModelSerializer):
    class Meta:
        model = Comment
        fields = ["name", "comment", "date"]


# single post serializer
class PostSerializer(ModelSerializer):

    # method field
    author = SerializerMethodField()
    paragraphs = ParagraphSerializer(many=True)
    comments = CommentSerializer(many=True)

    def get_author(self, Post):
        return Post.get_author()

    class Meta:
        model = Post
        fields = ["id", "image", "category", "featured", "title",
                  "date", "total_comments", "views", "tags", "author", "paragraphs", "comments"]

        read_only_fields = ['id', 'date', "total_comments"]


# mini post serializer
class PostSerializerMinified(PostSerializer):
    short_text = SerializerMethodField()

    def get_short_text(self, Post):
        return Post.get_short_text()

    class Meta:
        model = Post
        fields = ["id", "thumbnail", "category", "featured", "title",
                  "date", "total_comments", "views", 'short_text']

        read_only_fields = ['id', 'date']

# popular posts serializer


class PostSerializerMostViewed(PostSerializerMinified):
    class Meta:
        model = Post
        fields = ["id", "thumbnail", "category", "title",
                  "date", "total_comments", "views"]


class PostSerializerPopular(ModelSerializer):
    class Meta:
        model = Post
        fields = ["id", "thumbnail", "title", "category", "date"]


# Newsfeed
class NewsFeedSerializer(ModelSerializer):
    class Meta:
        model = NewsFeed
        fields = ["name", "email"]
