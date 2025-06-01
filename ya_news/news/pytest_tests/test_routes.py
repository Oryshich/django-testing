from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture as lf


pytestmark = pytest.mark.django_db


def test_pages_logout(client, get_users_logout_url):
    response = client.post(get_users_logout_url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'url, parametrized_client, expected_status',
    (
        (lf('get_news_edit_url'), lf('reader_client'), HTTPStatus.NOT_FOUND),
        (lf('get_news_delete_url'), lf('reader_client'), HTTPStatus.NOT_FOUND),
        (lf('get_news_edit_url'), lf('author_client'), HTTPStatus.OK),
        (lf('get_news_delete_url'), lf('author_client'), HTTPStatus.OK),
        (lf('get_news_detail_url'), lf('client'), HTTPStatus.OK),
        (lf('get_news_home_url'), lf('client'), HTTPStatus.OK),
        (lf('get_users_login_url'), lf('client'), HTTPStatus.OK),
        (lf('get_users_signup_url'), lf('client'), HTTPStatus.OK),
    ),
)
def test_availability_for_comment_edit_and_delete(
    url, parametrized_client, expected_status
):
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url',
    (
        lf('get_news_edit_url'),
        lf('get_news_delete_url')
    )
)
def test_redirect_for_anonymous_client(
    client, url, get_users_login_url
):
    expected_url = f'{get_users_login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
