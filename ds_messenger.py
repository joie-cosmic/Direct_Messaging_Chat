# a5.py
#
# ICS 32
# Assignment 5: Direct Messaging Chat
# Author: Joy Zhou
# Email: yunxinz6@uci.edu
# ID number: 32927020
# Description: GUI for direct messaging application
import socket
import json
import ds_protocol


class DirectMessage:
    '''Represents a single direct message'''

    def __init__(self):
        self.recipient = None
        self.message = None
        self.timestamp = None


class DirectMessenger:
    '''Handles sending and receiving direct messages with DSU server'''

    def __init__(self, dsuserver=None, username=None, password=None):
        self.dsuserver = dsuserver
        self.username = username
        self.password = password
        self.token = None
        self.token = self._join()

    def _join(self) -> str:
        '''
        Join the DSU server and retrieve token.
        Returns token string if successful, None if failed.
        '''
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.dsuserver, 2021))
                join = ds_protocol.join_msg(self.username, self.password)
                s.sendall(join.encode('utf-8') + b'\r\n')
                response = s.recv(4096).decode('utf-8')
                print(f"Join raw response: {response}")
                parsed = ds_protocol.extract_json(response)
                print(f"Join parsed: {parsed}")
                if parsed.type == 'ok':
                    return parsed.token
                return None
        except Exception as e:
            print(f"Join failed: {e}")
            return None

    def _send_to_server(self, message: str) -> dict:
        '''
        Connect to server, join, then send message.
        Returns parsed response dict.
        '''
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.dsuserver, 2021))

                join = ds_protocol.join_msg(self.username, self.password)
                s.sendall(join.encode('utf-8') + b'\r\n')
                join_response = s.recv(4096).decode('utf-8')
                print(f"Join response: {join_response}")
                parsed_join = ds_protocol.extract_json(join_response)
                print(f"Parsed join: {parsed_join}")

                if parsed_join.type == 'ok':
                    self.token = parsed_join.token
                else:
                    print("Join failed!")
                    return {}

                s.sendall(message.encode('utf-8') + b'\r\n')
                response = s.recv(4096).decode('utf-8')
                print(f"Send response: {response}")
                return ds_protocol.parse_response(response)

        except Exception as e:
            print(f"Send failed: {e}")
            return {}

    def send(self, message: str, recipient: str) -> bool:
        '''
        Send a direct message to recipient.
        Returns True if successful, False if failed.
        '''
        if self.token is None:
            return False
        msg = ds_protocol.send_directmessage(
            self.token, message, recipient
        )
        response = self._send_to_server(msg)
        return response.get('type') == 'ok'

    def retrieve_new(self) -> list:
        '''
        Retrieve new unread messages from server.
        Returns list of DirectMessage objects.
        '''
        if self.token is None:
            return []
        msg = ds_protocol.request_new_messages(self.token)
        response = self._send_to_server(msg)
        return self._build_message_list(response)

    def retrieve_all(self) -> list:
        '''
        Retrieve all messages from server.
        Returns list of DirectMessage objects.
        '''
        if self.token is None:
            return []
        msg = ds_protocol.request_all_messages(self.token)
        response = self._send_to_server(msg)
        return self._build_message_list(response)

    def _build_message_list(self, response: dict) -> list:
        '''
        Convert response dict into list of DirectMessage objects.
        '''
        result = []
        messages = response.get('messages', [])
        for m in messages:
            dm = DirectMessage()
            dm.message = m.get('message')
            dm.recipient = m.get('from')
            dm.timestamp = m.get('timestamp')
            result.append(dm)
        return result
