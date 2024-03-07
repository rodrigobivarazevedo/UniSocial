from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from .models import Email
from django.urls import reverse
import json


User = get_user_model()


class MailViewsTest(TestCase):
    def setUp(self):
        """Create a test user"""
        self.user = User.objects.create_user(username='test_user1', email="test_user1@example.com", password='password')
        user2 = User.objects.create_user(username='test_user2', email="test_user2@example.com" ,password='password')
        user3 = User.objects.create_user(username='test_user3', email="test_user3@example.com" ,password='password')
        self.client = Client()
        self.client.force_login(self.user)

    def test_mail_view_authenticated(self):
        """Test mail view for authenticated user"""
        response = self.client.get(reverse('mail'))
        self.assertEqual(response.status_code, 200)

    def test_mail_view_unauthenticated(self):
        """ Test mail view for unauthenticated user """
        self.client.logout()
        response = self.client.get(reverse('mail'))
        # Check if the response is a redirect
        self.assertRedirects(response, f'/login?next=/mail/', fetch_redirect_response=False)
        #self.assertRedirects(response, reverse('login'))

    def test_compose_view_get(self):
        """ Test compose view for GET request """
        response = self.client.get(reverse('compose'))
        self.assertEqual(response.status_code, 400)

    def test_compose_view_invalid_recipients(self):
        """ Test compose view with invalid recipients"""
        data = json.dumps({'recipients': ''})  # Ensure data is properly formatted as JSON
        response = self.client.post(reverse('compose'), data, content_type='application/json')
        self.assertEqual(response.status_code, 400)


    def test_compose_view_valid_recipient(self):
        """ Test compose view with one valid recipient"""
        data = {'recipients': 'test_user2@example.com', 'subject': 'Test', 'body': 'Test email body'}
        response = self.client.post(reverse('compose'), data, content_type='application/json')
        self.assertEqual(response.status_code, 201)

        # Check response content
        self.assertIn('message', response.json())
        self.assertEqual(response.json()['message'], 'Email sent successfully.')

        # Check database changes
        sent_email = Email.objects.first()
        self.assertIsNotNone(sent_email)
        self.assertEqual(sent_email.sender, self.user)
        self.assertEqual(sent_email.recipients.count(), 1)
        self.assertEqual(sent_email.recipients.first().email, 'test_user2@example.com')
        self.assertEqual(sent_email.subject, 'Test')
        self.assertEqual(sent_email.body, 'Test email body')

    def test_compose_view_valid_recipients(self):
        """ Test compose view with multiple valid recipients"""
        data = {'recipients': 'test_user2@example.com, test_user3@example.com', 'subject': 'Test', 'body': 'Test email body'}
        response = self.client.post(reverse('compose'), data, content_type='application/json')
        self.assertEqual(response.status_code, 201)

        # Check response content
        self.assertIn('message', response.json())
        self.assertEqual(response.json()['message'], 'Email sent successfully.')

        # Check database changes
        sent_email = Email.objects.first()
        self.assertIsNotNone(sent_email)
        self.assertEqual(sent_email.sender, self.user)
        self.assertEqual(sent_email.recipients.count(), 2)
        recipient_emails = [recipient.email for recipient in sent_email.recipients.all()]
        self.assertIn('test_user2@example.com', recipient_emails)
        self.assertIn('test_user3@example.com', recipient_emails)
        self.assertEqual(sent_email.subject, 'Test')
        self.assertEqual(sent_email.body, 'Test email body')

    def test_mailbox_view(self):
        """ Test mailbox view """
        data = {'recipients': 'test_user1@example.com', 'subject': 'Test', 'body': 'Test email body'}
        self.client.post(reverse('compose'), data, content_type='application/json')
        response = self.client.get(reverse('mailbox', args=['inbox']))
        self.assertEqual(response.status_code, 200)

        # Add more assertions as needed for the returned data
        self.assertTrue(response.json())  # the response should not be empty

    def test_email_view_get_error(self):
        """ Test email view for GET request"""
        response = self.client.get(reverse('email', args=[1]))
        self.assertEqual(response.status_code, 404)  # Assuming email with ID 1 does not exist

    def test_email_view_put_error(self):
        """ Test email view for PUT request """
        response = self.client.put(reverse('email', args=[1]), {'read': True}, content_type='application/json')
        self.assertEqual(response.status_code, 404) 


    def test_email_view_get(self):
        """ Test email view for GET request"""
        # Compose an email
        data = {'recipients': 'test_user2@example.com', 'subject': 'Test', 'body': 'Test email body'}
        self.client.post(reverse('compose'), data, content_type='application/json')

        # Retrieve the ID of the composed email
        email_id = Email.objects.first().id

        # Test email view for GET request
        response = self.client.get(reverse('email', args=[email_id]))
        self.assertEqual(response.status_code, 200)
        # Retrieve the ID of the composed email
        email_id = Email.objects.first().id

        # Check database changes
        sent_email = Email.objects.get(id=email_id)
        self.assertIsNotNone(sent_email)
        self.assertEqual(sent_email.sender, self.user)
        self.assertEqual(sent_email.recipients.count(), 1)
        self.assertEqual(sent_email.recipients.first().email, 'test_user2@example.com')
        self.assertEqual(sent_email.subject, 'Test')
        self.assertEqual(sent_email.body, 'Test email body')


    def test_email_view_put_mark_as_read(self):
        """ Test email view for PUT request to mark email as read """
        # Compose an email
        data = {'recipients': 'test_user2@example.com', 'subject': 'Test', 'body': 'Test email body'}
        self.client.post(reverse('compose'), data, content_type='application/json')

        # Retrieve the ID of the composed email
        email_id = Email.objects.first().id

        # Test email view for PUT request to mark email as read
        response = self.client.put(reverse('email', args=[email_id]), {'read': True}, content_type='application/json')
        self.assertEqual(response.status_code, 204)

        # Check if email is marked as read in the database
        updated_email = Email.objects.get(id=email_id)
        self.assertTrue(updated_email.read)

    def test_email_view_put_archive_email(self):
        """ Test email view for PUT request to archive email """
        # Compose an email
        data = {'recipients': 'test_user2@example.com', 'subject': 'Test', 'body': 'Test email body'}
        self.client.post(reverse('compose'), data, content_type='application/json')

        # Retrieve the ID of the composed email
        email_id = Email.objects.first().id

        # Test email view for PUT request to archive email
        response = self.client.put(reverse('email', args=[email_id]), {'archived': True}, content_type='application/json')
        self.assertEqual(response.status_code, 204)

        # Check if email is archived in the database
        updated_email = Email.objects.get(id=email_id)
        self.assertTrue(updated_email.archived)

