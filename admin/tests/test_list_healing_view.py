from mock import patch, Mock

from django.conf import settings
from django.test import TestCase
from django.test.client import RequestFactory

from admin.views import ListHealing


class ListHealingViewTest(TestCase):
    def setUp(self):
        self.request = RequestFactory().get("/")
        self.request.session = {"tsuru_token": "admin"}

    @patch("requests.get")
    def test_should_use_list_template(self, get):
        response_mock = Mock()
        response_mock.json.return_value = []
        get.return_value = response_mock
        response = ListHealing.as_view()(self.request)
        self.assertEqual("docker/list_healing.html", response.template_name)
        expected = []
        self.assertListEqual(expected, response.context_data["events"])
        get.assert_called_with(
            "{0}/docker/healing".format(settings.TSURU_HOST),
            headers={"authorization": "admin"}
        )
