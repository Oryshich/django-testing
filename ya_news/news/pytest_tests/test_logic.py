from http import HTTPStatus

from django.test import Client
from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


def test_anonymous_user_cant_create_comment(
        anonymous_client,
        new_item,
        form_data
):
    url = reverse('news:detail', args=(new_item.id,))
    anonymous_client.post(url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_can_create_comment(author, new_item, form_data):
    url = reverse('news:detail', args=(new_item.id,))
    client = Client()
    client.force_login(author)
    response = client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == new_item
    assert comment.author == author


def test_user_cant_use_bad_words(reader_client, new_item):
    url = reverse('news:detail', args=(new_item.id,))
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = reader_client.post(url, data=bad_words_data)
    assertFormError(
        response.context['form'],
        'text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(author_client, new_item, comment):
    news_url = reverse('news:detail', args=(new_item.id,))
    url_to_comments = news_url + '#comments'
    delete_url = reverse('news:delete', args=(comment.id,))
    response = author_client.delete(delete_url)
    assertRedirects(response, url_to_comments)
    assert response.status_code == HTTPStatus.FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_cant_delete_comment_of_another_user(
        reader_client,
        comment
):
    delete_url = reverse('news:delete', args=(comment.id,))
    response = reader_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_author_can_edit_comment(author_client, new_item, comment):
    NEW_COMMENT = {'text': 'Обновлённый комментарий'}
    news_url = reverse('news:detail', args=(new_item.id,))
    url_to_comments = news_url + '#comments'
    edit_url = reverse('news:edit', args=(comment.id,))
    response = author_client.post(edit_url, data=NEW_COMMENT)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == NEW_COMMENT['text']


def test_user_cant_edit_comment_of_another_user(reader_client, comment):
    NEW_COMMENT = {'text': 'Проверочный комментарий'}
    edit_url = reverse('news:edit', args=(comment.id,))
    response = reader_client.post(edit_url, data=NEW_COMMENT)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text != NEW_COMMENT['text']
