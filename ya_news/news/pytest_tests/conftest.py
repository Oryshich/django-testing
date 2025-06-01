from datetime import datetime, timedelta

from django.conf import settings
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone
from pytest import fixture

from news.models import Comment, News


@fixture
def new_item():
    new_item = News.objects.create(
        title='Заголовок',
        text='Текст новости',
    )
    return new_item


@fixture
def new_x_item():
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)


@fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@fixture
def reader(django_user_model):
    return django_user_model.objects.create(username='Читатель')


@fixture
def commentator(django_user_model):
    return django_user_model.objects.create(username='Комментатор')


@fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@fixture
def reader_client(reader):
    client = Client()
    client.force_login(reader)
    return client


@fixture
def comment(author, new_item):
    comment = Comment.objects.create(
        text='Текст комментария',
        news=new_item,
        author=author,
    )
    return comment


@fixture
def new_x_comment(new_item, commentator):
    now = timezone.now()
    for index in range(10):
        comment = Comment.objects.create(
            news=new_item, author=commentator, text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()


@fixture
def get_news_home_url():
    return reverse('news:home')


@fixture
def get_users_login_url():
    return reverse('users:login')


@fixture
def get_users_signup_url():
    return reverse('users:signup')


@fixture
def get_users_logout_url():
    return reverse('users:logout')


@fixture
def get_news_edit_url(comment):
    return reverse('news:edit', args=(comment.id,))


@fixture
def get_news_delete_url(comment):
    return reverse('news:delete', args=(comment.id,))


@fixture
def get_news_detail_url(new_item):
    return reverse('news:detail', args=(new_item.id,))
