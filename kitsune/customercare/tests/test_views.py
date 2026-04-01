from unittest.mock import patch

from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from kitsune.customercare.tests import SupportTicketFactory
from kitsune.users.tests import UserFactory


class TicketDetailViewTests(TestCase):
    def setUp(self):
        self.owner = UserFactory()
        self.other = UserFactory()
        self.ticket = SupportTicketFactory(user=self.owner)

    def test_owner_can_view(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse("customercare.ticket_detail", args=[self.owner.username, self.ticket.id]))
        self.assertEqual(200, response.status_code)

    def test_other_user_gets_404(self):
        self.client.force_login(self.other)
        response = self.client.get(reverse("customercare.ticket_detail", args=[self.owner.username, self.ticket.id]))
        self.assertEqual(404, response.status_code)

    def test_anonymous_redirects_to_login(self):
        response = self.client.get(reverse("customercare.ticket_detail", args=[self.owner.username, self.ticket.id]))
        self.assertEqual(302, response.status_code)
        self.assertIn("/users/login", response["Location"])

    def test_staff_can_view_any_ticket(self):
        staff = UserFactory()
        perm = Permission.objects.get(codename="change_supportticket")
        staff.user_permissions.add(perm)
        self.client.force_login(staff)
        response = self.client.get(reverse("customercare.ticket_detail", args=[self.owner.username, self.ticket.id]))
        self.assertEqual(200, response.status_code)

    def test_get_absolute_url(self):
        expected = reverse("customercare.ticket_detail", args=[self.owner.username, self.ticket.id])
        self.assertEqual(expected, self.ticket.get_absolute_url())

    def test_template_shows_subject(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse("customercare.ticket_detail", args=[self.owner.username, self.ticket.id]))
        self.assertContains(response, self.ticket.subject)

    def test_template_shows_description(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse("customercare.ticket_detail", args=[self.owner.username, self.ticket.id]))
        self.assertContains(response, self.ticket.description)

    def test_template_shows_status_badge(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse("customercare.ticket_detail", args=[self.owner.username, self.ticket.id]))
        self.assertContains(response, 'class="status-label')


class SyncTicketCommentsViewTests(TestCase):
    def setUp(self):
        self.owner = UserFactory()
        self.other = UserFactory()
        self.ticket = SupportTicketFactory(user=self.owner, zendesk_ticket_id="123")

    def _url(self):
        return reverse("customercare.ticket_detail", args=[self.owner.username, self.ticket.id])

    def _htmx_get(self):
        return self.client.get(self._url(), HTTP_HX_REQUEST="true")

    @patch("kitsune.customercare.views.sync_ticket_from_zendesk")
    def test_htmx_request_triggers_sync_and_returns_partial(self, mock_sync):
        self.client.force_login(self.owner)
        response = self._htmx_get()
        self.assertEqual(200, response.status_code)
        mock_sync.assert_called_once_with(self.ticket)

    @patch("kitsune.customercare.views.sync_ticket_from_zendesk")
    def test_zd_failure_returns_error_partial(self, mock_sync):
        mock_sync.side_effect = Exception("ZD unreachable")
        self.client.force_login(self.owner)
        response = self._htmx_get()
        self.assertEqual(200, response.status_code)
        self.assertContains(response, "latest replies")

    def test_non_owner_htmx_gets_404(self):
        self.client.force_login(self.other)
        response = self._htmx_get()
        self.assertEqual(404, response.status_code)

    def test_anonymous_htmx_redirects(self):
        response = self._htmx_get()
        self.assertEqual(302, response.status_code)
