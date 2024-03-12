from django.test import TestCase
from network.models import User
from .models import Email
from datetime import datetime



class MailTests(TestCase):
    def setUp(self):
        """
        This method sets up initial state for the tests by creating three users.
        """
        self.user3 = User.objects.create_user(username='user3', email='user3@example.com', password='password')
        self.user4 = User.objects.create_user(username='user4', email='user4@example.com', password='password')
        self.user5 = User.objects.create_user(username='user5', email='user5@example.com', password='password')

    def test_email_creation_single_recipient(self):
        """
        Tests whether an Email object can be created successfully with a single recipient.
        """
        email = Email.objects.create(user=self.user3, sender=self.user4, subject="Test Subject", body="Test Body")
        email.recipients.add(self.user3)  # Add recipient
        self.assertEqual(email.user, self.user3)
        self.assertEqual(email.sender, self.user4)
        self.assertIn(self.user3, email.recipients.all())
        self.assertEqual(email.subject, "Test Subject")
        self.assertEqual(email.body, "Test Body")
        self.assertTrue(isinstance(email.timestamp, datetime))
        self.assertFalse(email.read)
        self.assertFalse(email.archived)

        # Test serialization
        serialized_email = email.serialize()
        self.assertEqual(serialized_email['id'], email.id)
        self.assertEqual(serialized_email['user'], self.user3.username)
        self.assertEqual(serialized_email['sender'], self.user4.username)
        self.assertEqual(set(serialized_email['recipients']), {self.user3.username})  # Check recipients as set
        self.assertEqual(serialized_email['subject'], "Test Subject")
        self.assertEqual(serialized_email['body'], "Test Body")
        self.assertEqual(serialized_email['read'], False)
        self.assertEqual(serialized_email['archived'], False)
        # Ensure timestamp is formatted correctly
        expected_timestamp = email.timestamp.strftime("%b %d %Y, %I:%M %p")
        self.assertEqual(serialized_email['timestamp'], expected_timestamp)

    def test_email_creation_multiple_recipients(self):
        """
        Tests whether an Email object can be created successfully with multiple recipients.
        """
        email = Email.objects.create(user=self.user3, sender=self.user4, subject="Test Subject", body="Test Body")
        email.recipients.add(self.user3)  # Add first recipient
        email.recipients.add(self.user5)  # Add second recipient
        self.assertEqual(email.user, self.user3)
        self.assertEqual(email.sender, self.user4)
        self.assertIn(self.user3, email.recipients.all())
        self.assertIn(self.user5, email.recipients.all())  # Check for second recipient
        self.assertEqual(email.subject, "Test Subject")
        self.assertEqual(email.body, "Test Body")
        self.assertTrue(isinstance(email.timestamp, datetime))
        self.assertFalse(email.read)
        self.assertFalse(email.archived)

        # Test serialization
        serialized_email = email.serialize()
        self.assertEqual(serialized_email['id'], email.id)
        self.assertEqual(serialized_email['user'], self.user3.username)
        self.assertEqual(serialized_email['sender'], self.user4.username)
        self.assertEqual(set(serialized_email['recipients']), {self.user3.username, self.user5.username})  # Check recipients as set
        self.assertEqual(serialized_email['subject'], "Test Subject")
        self.assertEqual(serialized_email['body'], "Test Body")
        self.assertEqual(serialized_email['read'], False)
        self.assertEqual(serialized_email['archived'], False)
        # Ensure timestamp is formatted correctly
        expected_timestamp = email.timestamp.strftime("%b %d %Y, %I:%M %p")
        self.assertEqual(serialized_email['timestamp'], expected_timestamp)
