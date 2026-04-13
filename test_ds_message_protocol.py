# a5.py
#
# ICS 32
# Assignment 5: Direct Messaging Chat
# Author: Joy Zhou
# Email: yunxinz6@uci.edu
# ID number: 32927020
# Description: GUI for direct messaging application
import unittest
import json
import ds_protocol


class TestDSProtocol(unittest.TestCase):

    def test_send_directmessage_format(self):
        '''Test that send_directmessage returns valid JSON'''
        result = ds_protocol.send_directmessage(
            "test_token", "Hello!", "ohhimark"
        )
        parsed = json.loads(result)
        self.assertEqual(parsed["token"], "test_token")
        self.assertEqual(parsed["directmessage"]["entry"], "Hello!")
        self.assertEqual(parsed["directmessage"]["recipient"], "ohhimark")

    def test_send_directmessage_has_timestamp(self):
        '''Test that send_directmessage includes a timestamp'''
        result = ds_protocol.send_directmessage(
            "test_token", "Hello!", "ohhimark"
        )
        parsed = json.loads(result)
        self.assertIn("timestamp", parsed["directmessage"])

    def test_request_new_messages_format(self):
        '''Test that request_new_messages returns valid JSON'''
        result = ds_protocol.request_new_messages("test_token")
        parsed = json.loads(result)
        self.assertEqual(parsed["token"], "test_token")
        self.assertEqual(parsed["directmessage"], "new")

    def test_request_all_messages_format(self):
        '''Test that request_all_messages returns valid JSON'''
        result = ds_protocol.request_all_messages("test_token")
        parsed = json.loads(result)
        self.assertEqual(parsed["token"], "test_token")
        self.assertEqual(parsed["directmessage"], "all")

    def test_parse_response_ok(self):
        '''Test parsing a valid ok response'''
        json_str = ('{"response": {"type": "ok", '
                    '"message": "Direct message sent"}}')
        result = ds_protocol.parse_response(json_str)
        self.assertEqual(result["type"], "ok")
        self.assertEqual(result["message"], "Direct message sent")

    def test_parse_response_empty_on_bad_json(self):
        '''Test that parse_response returns empty dict on bad JSON'''
        result = ds_protocol.parse_response("not valid json")
        self.assertEqual(result, {})

    def test_extract_messages_ok(self):
        '''Test extracting messages from a valid response'''
        json_str = json.dumps({
            "response": {
                "type": "ok",
                "messages": [
                    {
                        "message": "Hello!",
                        "from": "bob",
                        "timestamp": "1603167689.3928561"
                    },
                    {
                        "message": "Bye!",
                        "from": "alice",
                        "timestamp": "1603167699.3928561"
                    }
                ]
            }
        })
        result = ds_protocol.extract_messages(json_str)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["from"], "bob")
        self.assertEqual(result[1]["message"], "Bye!")

    def test_extract_messages_empty_on_error(self):
        '''Test that extract_messages returns empty list on bad JSON'''
        result = ds_protocol.extract_messages("not valid json")
        self.assertEqual(result, [])

    def test_extract_messages_empty_on_no_messages(self):
        '''Test that extract_messages returns empty list when no messages'''
        json_str = '{"response": {"type": "ok", "messages": []}}'
        result = ds_protocol.extract_messages(json_str)
        self.assertEqual(result, [])

    def test_join_msg_format(self):
        '''Test that join_msg returns valid JSON'''
        result = ds_protocol.join_msg("joy", "password123")
        parsed = json.loads(result)
        self.assertEqual(parsed["join"]["username"], "joy")
        self.assertEqual(parsed["join"]["password"], "password123")


if __name__ == "__main__":
    unittest.main()
