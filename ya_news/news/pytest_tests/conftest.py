from datetime import datetime, timedelta

from django.conf import settings
from django.test.client import Client
from django.utils import timezone
import pytest

from news.models import Comment, News


@pytest.fixture
def new_item():
    new_item = News.objects.create(
        title='Заголовок',
        text='Текст новости',
    )
    return new_item


@pytest.fixture
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
    return all_news


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create(username='Читатель')


@pytest.fixture
def commentator(django_user_model):
    return django_user_model.objects.create(username='Комментатор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def anonymous_client(reader):
    client = Client()
    return client


@pytest.fixture
def reader_client(reader):
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def comment(author, new_item):
    comment = Comment.objects.create(
        text='Текст комментария',
        news=new_item,
        author=author,
    )
    return comment


@pytest.fixture
def new_x_comment(new_item, commentator):
    now = timezone.now()
    for index in range(10):
        comment = Comment.objects.create(
            news=new_item, author=commentator, text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()
    return new_item.id


@pytest.fixture
def form_data():
    return {
        'text': 'Текст комментария'
    }
