import pytest
from django.conf import settings

from news.forms import CommentForm


pytestmark = pytest.mark.django_db


def test_news_count(new_x_item, reader_client, get_news_home_url):
    response = reader_client.get(get_news_home_url)
    news_count = response.context['object_list'].count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(new_x_item, reader_client, get_news_home_url):
    response = reader_client.get(get_news_home_url)
    all_dates = [news.date for news in response.context['object_list']]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(new_x_comment, author_client, get_news_detail_url):
    response = author_client.get(get_news_detail_url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


def test_anonymous_client_has_no_form(client, get_news_detail_url):
    response = client.get(get_news_detail_url)
    assert 'form' not in response.context


def test_authorized_client_has_form(reader_client, get_news_detail_url):
    response = reader_client.get(get_news_detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
