from django.db.models import Count, Q
from rest_framework.views import Response

from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, CreateModelMixin
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny

from datetime import date

from app.settings import DEBUG
from .models import Paragraph, Post, Comment, NewsFeed
from .serializers import PostSerializer, PostSerializerMinified, CommentSerializer, PostSerializerMostViewed, PostSerializerPopular, NewsFeedSerializer

# Create your views here.


class SmallResultSetPagination(PageNumberPagination):
    page_size = 6


class PostViewSet(GenericViewSet, ListModelMixin, CreateModelMixin):
    serializer_class = PostSerializerMinified
    queryset = Post.objects.all()
    permission_classes = [AllowAny]

# posts filter

    @ action(["get"], detail=False)
    def filter(self, request, *args, **kwargs):
        self.serializer_class = PostSerializerMinified

        # related posts
        if (related_category := request.query_params.get('relatedcategory')):
            # custom pagination
            self.pagination_class = SmallResultSetPagination

            tagslist = request.query_params.get('relatedtag').split(",")

            self.queryset = self.queryset.filter(
                category__iexact=related_category).exclude(id=request.query_params.get('id'))

            self.queryset = self.queryset.filter(Q(tags__icontains=tagslist[0]) | Q(
                tags__icontains=tagslist[1]) | Q(tags__icontains=tagslist[2]))
            if not DEBUG:
                self.queryset = self.queryset.distinct("id").orderby("-1d")

        # category
        elif request.query_params.get('category'):
            category = request.query_params.get('category')
            try:
                year = int(category)
                self.queryset = self.queryset.filter(
                    date__year=year)
            except:
                self.queryset = self.queryset.filter(
                    category__iexact=category)

        # featured
        elif request.query_params.get('featured'):
            # custom pagination
            self.pagination_class = SmallResultSetPagination
            category = request.query_params.get('featured')

            try:
                year = int(category)
                self.queryset = self.queryset.filter(
                    featured=True, date__year=year)
            except:
                self.queryset = self.queryset.filter(
                    featured=True) if category == "all" else self.queryset.filter(
                    featured=True, category__iexact=category)

        # popular
        elif request.query_params.get('popular'):
            # custom pagination and serializer
            self.serializer_class = PostSerializerPopular
            self.pagination_class = SmallResultSetPagination

            category = request.query_params.get('popular')
            id = request.query_params.get('id')
            today = date.today()

            self.queryset = self.queryset.annotate(
                total_comments=Count('comments'))

            try:
                year = int(category)
                self.queryset = self.queryset.filter(
                    date__year=year).order_by("-total_comments")
            except:
                self.queryset = self.queryset.filter(
                    date__year=today.year).order_by("-total_comments") if category == "all" else self.queryset.filter(category__iexact=category, date__year=today.year).order_by("-total_comments")

                if id:
                    self.queryset = self.queryset.exclude(pk=id)

        # most viewed
        elif request.query_params.get('most_viewed'):
            self.serializer_class = PostSerializerMostViewed
            category = request.query_params.get('most_viewed')
            today = date.today()

            try:
                year = int(category)
                self.queryset = self.queryset.filter(
                    date__year=year).order_by("-views")
            except:
                self.queryset = self.queryset.filter(
                    date__year=today.year).order_by("-views") if category == "all" else self.queryset.filter(category__iexact=category).filter(
                    date__year=today.year).order_by("-views")

        # category counts
        elif request.query_params.get('category_count'):
            query_set = self.queryset.values("category")

            self.queryset = [
                {
                    "text": "design",
                    "count": query_set.filter(
                        category='design'
                    ).count()
                },
                {
                    "text": "fashion",
                    "count": query_set.filter(
                        category='fashion'
                    ).count()
                },

                {
                    "text": "lifestyle",
                    "count": query_set.filter(
                        category='lifestyle'
                    ).count()
                },
                {
                    "text": "talks",
                    "count": query_set.filter(
                        category='talks'
                    ).count()
                }
            ]

            return Response(self.queryset, status=200)

        # archives_count
        elif request.query_params.get('archives_count'):
            currentyear = date.today().year

            query_set = self.queryset.values("date")
            self.queryset = [
                {
                    "text": currentyear,
                    "count": query_set.filter(
                        date__year=currentyear
                    ).count()
                },
                {
                    "text": currentyear-1,
                    "count": query_set.filter(
                        date__year=currentyear-1
                    ).count()
                },
                {
                    "text": currentyear-2,
                    "count": query_set.filter(
                        date__year=currentyear-2
                    ).count()
                },
                {
                    "text": currentyear-3,
                    "count": query_set.filter(
                        date__year=currentyear-3
                    ).count()
                },
                {
                    "text": currentyear-4,
                    "count": query_set.filter(
                        date__year=currentyear-4
                    ).count()
                }
            ]
            return Response(self.queryset, status=200)

        # search
        elif request.query_params.get('search'):
            if (request.query_params.get('tagonly')):
                self.queryset = self.queryset.filter(tags__icontains=request.query_params.get(
                    'search'))

            else:
                self.queryset = self.queryset.filter(Q(title__icontains=request.query_params.get(
                    'search')) | Q(category__icontains=request.query_params.get('search')) | Q(tags__icontains=request.query_params.get(
                        'search')))

                if not DEBUG:
                    # print(Paragraph.objects.filter(
                    #     text__icontains=get('search')).distinct("id"))
                    # does not work for sqllite
                    self.queryset = self.queryset.distinct(
                        'id').order_by('-id')

        return self.list(request, *args, **kwargs)


# single post details

    @ action(["get"], detail=False)
    def singlepost(self, request, *args, **kwargs):

        self.serializer_class = PostSerializer

        if request.method == "GET":
            self.queryset = self.queryset.filter(
                pk=request.query_params.get('id'), category=request.query_params.get('category'))
            self.queryset[0].update_views()

            return self.list(request, *args, **kwargs)

# comment
    @ action(["post", "get"], detail=False)
    def comment(self, request, *args, **kwargs):
        self.serializer_class = CommentSerializer

        if request.method == "POST":
            # create comment
            (get_object_or_404(Post, pk=request.data["id"])).create_comment(
                request.data["name"], request.data["comment"])

            # return comments
            self.queryset = Comment.objects.filter(
                post=request.data["id"])

            return self.list(request, *args, **kwargs)


# subscribe to news feed


class NewsFeedViewset(GenericViewSet, CreateModelMixin):
    permission_classes = [AllowAny]
    queryset = NewsFeed.objects.all()
    serializer_class = NewsFeedSerializer
