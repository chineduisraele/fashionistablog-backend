from django.http import JsonResponse
from django.db.models import Count, Q

from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, CreateModelMixin
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny

from datetime import date
from .models import Post, Comment, NewsFeed
from .serializers import PostSerializer, PostSerializerMinified, CommentSerializer, PostSerializerMostViewed, PostSerializerPopular, NewsFeedSerializer

# Create your views here.


class SmallResulsSetPagination(PageNumberPagination):
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
        if request.query_params.get('relatedcategory'):
            # custom pagination
            self.pagination_class = SmallResulsSetPagination

            self.queryset = self.queryset.filter(
                category__iexact=request.query_params.get('relatedcategory')).exclude(id=request.query_params.get('id'))

            tagslist = request.query_params.get('relatedtag').split(",")

            self.queryset = self.queryset.filter(Q(tags__icontains=tagslist[0]) | Q(
                tags__icontains=tagslist[1]) | Q(tags__icontains=tagslist[2]))
            # add distinct() method

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

            category = request.query_params.get('featured').lower()

            try:
                year = int(category)
                self.queryset = self.queryset.filter(
                    featured=True).filter(
                    date__year=year)
            except:
                self.queryset = self.queryset.filter(
                    featured=True) if category == "all" else self.queryset.filter(
                    featured=True).filter(category=category)
            # custom pagination
            self.pagination_class = SmallResulsSetPagination

        # popular
        elif request.query_params.get('popular'):
            category = request.query_params.get('popular').lower()
            id = request.query_params.get('id')
            self.queryset = self.queryset.annotate(
                total_comments=Count('comments'))

            today = date.today()

            try:
                year = int(category)
                self.queryset = self.queryset.filter(
                    date__year=year).order_by("-total_comments")
            except:
                self.queryset = self.queryset.filter(
                    date__year=today.year).order_by("-total_comments") if category == "all" else self.queryset.filter(category=category).filter(
                    date__year=today.year).order_by("-total_comments")

                if id:
                    self.queryset = self.queryset.exclude(pk=id)

            # custom pagination and serializer
            self.serializer_class = PostSerializerPopular
            self.pagination_class = SmallResulsSetPagination

        # most viewed
        elif request.query_params.get('most_viewed'):
            category = request.query_params.get('most_viewed').lower()

            today = date.today()

            try:
                year = int(category)
                self.queryset = self.queryset.filter(
                    date__year=year).order_by("-views")
            except:
                self.queryset = self.queryset.filter(
                    date__year=today.year).order_by("-views") if category == "all" else self.queryset.filter(category=category).filter(
                    date__year=today.year).order_by("-views")

            self.serializer_class = PostSerializerMostViewed

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

            return JsonResponse(self.queryset, safe=False)

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

            return JsonResponse(self.queryset, safe=False)

        # search
        elif request.query_params.get('search'):
            if (request.query_params.get('tagonly')):
                self.queryset = self.queryset.filter(tags__icontains=request.query_params.get(
                    'search'))

            else:
                set1 = self.queryset.filter(title__icontains=request.query_params.get(
                    'search'))
                set2 = self.queryset.filter(
                    category__icontains=request.query_params.get('search'))
                set3 = self.queryset.filter(tags__icontains=request.query_params.get(
                    'search'))

                self.queryset = set1 | set2 | set3
            # use this when i change to mysql or postgre
            # self.queryset = (set1 | set2 | set3).distinct(
            #     'id').order_by('-id')

        return self.list(request, *args, **kwargs)


# single post details

    @ action(["get"], detail=False)
    def singlepost(self, request, *args, **kwargs):

        self.serializer_class = PostSerializer
        self.queryset = self.queryset.filter(
            pk=request.query_params.get('id'))

        if request.method == "GET":
            (get_object_or_404(Post, pk=request.query_params.get(
                'id'))).update_views()

            return self.list(request, *args, **kwargs)

# comment
    @ action(["post", "get"], detail=False)
    def comment(self, request, *args, **kwargs):
        self.serializer_class = CommentSerializer

        if request.method == "POST":
            self.queryset = Comment.objects.filter(
                post=request.data["id"])

            (get_object_or_404(Post, pk=request.data["id"])).create_comment(
                request.data["name"], request.data["comment"])

            return self.list(request, *args, **kwargs)


# subscribe to news feed


class NewsFeedViewset(GenericViewSet, CreateModelMixin):
    permission_classes = [AllowAny]
    queryset = NewsFeed.objects.all()
    serializer_class = NewsFeedSerializer
