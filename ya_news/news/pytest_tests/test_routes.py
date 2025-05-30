from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'url',
    (
        pytest.lazy_fixture('get_news_home_url'),
        pytest.lazy_fixture('get_users_login_url'),
        pytest.lazy_fixture('get_users_signup_url')
    )
)
def test_pages_availability_for_anonymous_user(client, url):
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


def test_pages_logout(client, get_users_logout_url):
    response = client.post(get_users_logout_url)
    assert response.status_code == HTTPStatus.OK


def test_pages_news_detail(client, get_news_detail_url):
    response = client.get(get_news_detail_url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('reader_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'url',
    (
        pytest.lazy_fixture('get_news_edit_url'),
        pytest.lazy_fixture('get_news_delete_url')
    ),
)
def test_availability_for_comment_edit_and_delete(
    parametrized_client, url, expected_status
):
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url',
    (
        pytest.lazy_fixture('get_news_edit_url'),
        pytest.lazy_fixture('get_news_delete_url')
    )
)
def test_redirect_for_anonymous_client(
    client, url, get_users_login_url
):
    expected_url = f'{get_users_login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
