from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

FORM_DATA = {'text': 'Текст комментария'}
pytestmark = pytest.mark.django_db


def test_anonymous_user_cant_create_comment(client, get_news_detail_url):
    comments_count = Comment.objects.count()
    client.post(get_news_detail_url, data=FORM_DATA)
    comments_count = Comment.objects.count() - comments_count
    assert comments_count == 0


def test_user_can_create_comment(
        author,
        author_client,
        new_item,
        get_news_detail_url
):
    url = get_news_detail_url
    Comment.objects.all().delete()
    response = author_client.post(url, data=FORM_DATA)
    assertRedirects(response, f'{url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == FORM_DATA['text']
    assert comment.news == new_item
    assert comment.author == author


def test_user_cant_use_bad_words(reader_client, get_news_detail_url):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    comments_count = Comment.objects.count()
    response = reader_client.post(get_news_detail_url, data=bad_words_data)
    comments_count = Comment.objects.count() - comments_count
    assert comments_count == 0
    assertFormError(
        response.context['form'],
        'text',
        errors=WARNING
    )


def test_author_can_delete_comment(
        author_client,
        get_news_detail_url,
        get_news_delete_url
):
    url_to_comments = get_news_detail_url + '#comments'
    comments_count = Comment.objects.count()
    response = author_client.delete(get_news_delete_url)
    assertRedirects(response, url_to_comments)
    assert response.status_code == HTTPStatus.FOUND
    comments_count = Comment.objects.count() - comments_count + 1
    assert comments_count == 0


def test_user_cant_delete_comment_of_another_user(
        reader_client,
        get_news_delete_url
):
    comments_count = Comment.objects.count()
    response = reader_client.delete(get_news_delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count() - comments_count
    assert comments_count == 0


def test_author_can_edit_comment(
        author_client,
        comment,
        get_news_detail_url,
        get_news_edit_url
):
    NEW_COMMENT = {'text': 'Обновлённый комментарий'}
    url_to_comments = get_news_detail_url + '#comments'
    response = author_client.post(get_news_edit_url, data=NEW_COMMENT)
    assertRedirects(response, url_to_comments)
    comment_after = Comment.objects.get(pk=comment.id)
    assert comment_after.text == NEW_COMMENT['text']
    assert comment_after.author == comment.author
    assert comment_after.news == comment.news


def test_user_cant_edit_comment_of_another_user(
        reader_client,
        comment,
        get_news_edit_url
):
    NEW_COMMENT = {'text': 'Проверочный комментарий'}
    response = reader_client.post(get_news_edit_url, data=NEW_COMMENT)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_after = Comment.objects.get(pk=comment.id)
    assert comment_after.text == comment.text
    assert comment_after.author == comment.author
    assert comment_after.news == comment.news
