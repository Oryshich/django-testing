from http import HTTPStatus

from .test_base import TestBaseNotePage


class TestRoutes(TestBaseNotePage):

    def test_pages_availability(self):
        urls = (
            self.notes_home_url,
            self.users_login_url,
            self.users_signup_url
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_page_logout_availability(self):
        response = self.not_author_client.post(self.users_logout_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        urls = (
            self.notes_list_url,
            self.notes_add_url,
            self.notes_success_url
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.not_author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_different_users(self):
        urls = (
            self.notes_detail_url,
            self.notes_edit_url,
            self.notes_delete_url)
        users_statuses = (
            (self.author_client, HTTPStatus.OK),
            (self.not_author_client, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            for url in urls:
                with self.subTest(user=user, url=url):
                    response = user.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirects(self):
        urls = (
            self.notes_detail_url,
            self.notes_edit_url,
            self.notes_delete_url,
            self.notes_add_url,
            self.notes_success_url,
            self.notes_list_url,
        )
        for url in urls:
            with self.subTest(url=url):
                expected_url = f'{self.users_login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, expected_url)
