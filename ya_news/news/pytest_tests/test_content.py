from django.conf import settings
from django.urls import reverse
import pytest

from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count(new_x_item, reader_client):
    url = reverse('news:home')
    response = reader_client.get(url)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(new_x_item, reader_client):
    url = reverse('news:home')
    response = reader_client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(new_x_comment, author_client):
    detail_url = reverse('news:detail', args=(new_x_comment,))
    response = author_client.get(detail_url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.django_db
def test_anonymous_client_has_no_form(new_x_comment, anonymous_client):
    detail_url = reverse('news:detail', args=(new_x_comment,))
    response = anonymous_client.get(detail_url)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_authorized_client_has_form(new_x_comment, reader_client):
    detail_url = reverse('news:detail', args=(new_x_comment,))
    response = reader_client.get(detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
