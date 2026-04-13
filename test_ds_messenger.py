# a5.py
#
# ICS 32
# Assignment 5: Direct Messaging Chat
# Author: Joy Zhou
# Email: yunxinz6@uci.edu
# ID number: 32927020
# Description: GUI for direct messaging application
import unittest
from unittest.mock import patch, MagicMock
from ds_messenger import DirectMessage, DirectMessenger


class TestDirectMessage(unittest.TestCase):

    def test_direct_message_init(self):
        '''Test DirectMessage initializes with None values'''
        dm = DirectMessage()
        self.assertIsNone(dm.recipient)
        self.assertIsNone(dm.message)
        self.assertIsNone(dm.timestamp)

    def test_direct_message_set_values(self):
        '''Test DirectMessage can store values'''
        dm = DirectMessage()
        dm.recipient = "bob"
        dm.message = "Hello!"
        dm.timestamp = "1603167689.3928561"
        self.assertEqual(dm.recipient, "bob")
        self.assertEqual(dm.message, "Hello!")
        self.assertEqual(dm.timestamp, "1603167689.3928561")


class TestDirectMessenger(unittest.TestCase):

    def setUp(self):
        '''
        Run before every test.
        We mock the socket so we dont need a real server.
        '''
        self.mock_join_response = ('{"response": {"type": "ok", '
                                   '"message": "Welcome!", "token": '
                                   '"fake_token_123"}}')
        self.mock_send_response = ('{"response": {"type": "ok", "message": '
                                   '"Direct message sent"}}')
        self.mock_messages_response = ('{"response": {"type": '
                                       '"ok", "messages":'
                                       ' [{"message": "Hi!", '
                                       '"from": "alice", "timestamp": '
                                       '"1603167689.3928561"}, {"message": '
                                       '"Hey!", "from": "bob", "timestamp": '
                                       '"1603167699.3928561"}]}}')
        self.mock_empty_response = ('{"response": {"type": "ok", '
                                    '"messages": []}}')

    @patch('socket.socket')
    def _make_messenger(self, mock_socket_class, join_response=None):
        '''
        Helper: create a DirectMessenger with mocked socket.
        '''
        if join_response is None:
            join_response = self.mock_join_response

        mock_socket = MagicMock()
        mock_socket_class.return_value.__enter__.return_value = mock_socket
        mock_socket.recv.return_value = join_response.encode('utf-8')

        messenger = DirectMessenger(
            dsuserver="fake_server",
            username="joy",
            password="password123"
        )
        return messenger

    @patch('socket.socket')
    def test_messenger_init_success(self, mock_socket_class):
        '''Test DirectMessenger initializes and gets token'''
        mock_socket = MagicMock()
        mock_socket_class.return_value.__enter__.return_value = mock_socket
        mock_socket.recv.return_value = self.mock_join_response.encode('utf-8')

        messenger = DirectMessenger(
            dsuserver="fake_server",
            username="joy",
            password="password123"
        )
        self.assertEqual(messenger.token, "fake_token_123")

    @patch('socket.socket')
    def test_messenger_init_fail(self, mock_socket_class):
        '''Test DirectMessenger handles failed join'''
        mock_socket = MagicMock()
        mock_socket_class.return_value.__enter__.return_value = mock_socket
        mock_socket.recv.return_value = (b'{"response": {"type": "error", '
                                         b'"message": "Failed"}}')

        messenger = DirectMessenger(
            dsuserver="fake_server",
            username="joy",
            password="wrongpassword"
        )
        self.assertIsNone(messenger.token)

    @patch('socket.socket')
    def test_send_returns_true_on_success(self, mock_socket_class):
        '''Test send() returns True when server responds ok'''
        mock_socket = MagicMock()
        mock_socket_class.return_value.__enter__.return_value = mock_socket
        mock_socket.recv.side_effect = [
            self.mock_join_response.encode('utf-8'),  # join response
            self.mock_send_response.encode('utf-8')   # send response
        ]

        messenger = DirectMessenger(
            dsuserver="fake_server",
            username="joy",
            password="password123"
        )
        messenger.token = "fake_token_123"

        mock_socket.recv.side_effect = [
            self.mock_join_response.encode('utf-8'),
            self.mock_send_response.encode('utf-8')
        ]
        result = messenger.send("Hello!", "bob")
        self.assertTrue(result)

    @patch('socket.socket')
    def test_send_returns_false_on_failure(self, mock_socket_class):
        '''Test send() returns False when server responds error'''
        mock_socket = MagicMock()
        mock_socket_class.return_value.__enter__.return_value = mock_socket
        mock_socket.recv.side_effect = [
            self.mock_join_response.encode('utf-8'),
            b'{"response": {"type": "error", "message": "Failed"}}'
        ]

        messenger = DirectMessenger(
            dsuserver="fake_server",
            username="joy",
            password="password123"
        )
        messenger.token = "fake_token_123"

        mock_socket.recv.side_effect = [
            self.mock_join_response.encode('utf-8'),
            b'{"response": {"type": "error", "message": "Failed"}}'
        ]
        result = messenger.send("Hello!", "bob")
        self.assertFalse(result)

    @patch('socket.socket')
    def test_retrieve_all_returns_list(self, mock_socket_class):
        '''Test retrieve_all() returns list of DirectMessage objects'''
        mock_socket = MagicMock()
        mock_socket_class.return_value.__enter__.return_value = mock_socket
        mock_socket.recv.side_effect = [
            self.mock_join_response.encode('utf-8'),
            self.mock_join_response.encode('utf-8'),
            self.mock_messages_response.encode('utf-8')
        ]

        messenger = DirectMessenger(
            dsuserver="fake_server",
            username="joy",
            password="password123"
        )
        messenger.token = "fake_token_123"

        mock_socket.recv.side_effect = [
            self.mock_join_response.encode('utf-8'),
            self.mock_messages_response.encode('utf-8')
        ]
        result = messenger.retrieve_all()
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], DirectMessage)
        self.assertEqual(result[0].recipient, "alice")
        self.assertEqual(result[0].message, "Hi!")

    @patch('socket.socket')
    def test_retrieve_new_returns_list(self, mock_socket_class):
        '''Test retrieve_new() returns list of DirectMessage objects'''
        mock_socket = MagicMock()
        mock_socket_class.return_value.__enter__.return_value = mock_socket

        messenger = DirectMessenger(
            dsuserver="fake_server",
            username="joy",
            password="password123"
        )
        messenger.token = "fake_token_123"

        mock_socket.recv.side_effect = [
            self.mock_join_response.encode('utf-8'),
            self.mock_messages_response.encode('utf-8')
        ]
        result = messenger.retrieve_new()
        self.assertIsInstance(result, list)

    @patch('socket.socket')
    def test_retrieve_all_empty(self, mock_socket_class):
        '''Test retrieve_all() returns empty list when no messages'''
        mock_socket = MagicMock()
        mock_socket_class.return_value.__enter__.return_value = mock_socket

        messenger = DirectMessenger(
            dsuserver="fake_server",
            username="joy",
            password="password123"
        )
        messenger.token = "fake_token_123"

        mock_socket.recv.side_effect = [
            self.mock_join_response.encode('utf-8'),
            self.mock_empty_response.encode('utf-8')
        ]
        result = messenger.retrieve_all()
        self.assertEqual(result, [])

    def test_send_no_token_returns_false(self):
        '''Test send() returns False when token is None'''
        messenger = DirectMessenger.__new__(DirectMessenger)
        messenger.token = None
        result = messenger.send("Hello!", "bob")
        self.assertFalse(result)

    def test_retrieve_all_no_token_returns_empty(self):
        '''Test retrieve_all() returns empty list when token is None'''
        messenger = DirectMessenger.__new__(DirectMessenger)
        messenger.token = None
        result = messenger.retrieve_all()
        self.assertEqual(result, [])

    def test_retrieve_new_no_token_returns_empty(self):
        '''Test retrieve_new() returns empty list when token is None'''
        messenger = DirectMessenger.__new__(DirectMessenger)
        messenger.token = None
        result = messenger.retrieve_new()
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
