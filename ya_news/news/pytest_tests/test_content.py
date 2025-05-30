import pytest
from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm


pytestmark = pytest.mark.django_db


def test_news_count(new_x_item, reader_client, get_news_home_url):
    response = reader_client.get(get_news_home_url)
    news_count = response.context['object_list'].count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(new_x_item, reader_client, get_news_home_url):
    response = reader_client.get(get_news_home_url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(new_x_comment, author_client):
    detail_url = reverse('news:detail', args=(new_x_comment,))
    response = author_client.get(detail_url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


def test_anonymous_client_has_no_form(new_x_comment, client):
    detail_url = reverse('news:detail', args=(new_x_comment,))
    response = client.get(detail_url)
    assert 'form' not in response.context


def test_authorized_client_has_form(new_x_comment, reader_client):
    detail_url = reverse('news:detail', args=(new_x_comment,))
    response = reader_client.get(detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
