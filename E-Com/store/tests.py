from django.test import SimpleTestCase


class ApiRootTests(SimpleTestCase):
    def test_api_root_supports_json_clients(self):
        response = self.client.get('/', HTTP_ACCEPT='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['store'], '/api/store/')

    def test_api_root_supports_browser_html_requests(self):
        response = self.client.get('/', HTTP_ACCEPT='text/html')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '/api/store/')
