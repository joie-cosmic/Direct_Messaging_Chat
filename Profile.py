# Profile.py
#
# ICS 32
# Assignment #5: Direct Messaging Chat
#
# Author: Mark S. Baldwin, modified by Alberto Krone-Martins
#
# v0.1.9

import json
import time
from pathlib import Path


class DsuFileError(Exception):
    pass


class DsuProfileError(Exception):
    pass


class Post(dict):
    """
    The Post class is responsible for working with individual user posts.
    """
    def __init__(self, entry: str = None, timestamp: float = 0):
        self._timestamp = timestamp
        self.set_entry(entry)
        dict.__init__(self, entry=self._entry, timestamp=self._timestamp)

    def set_entry(self, entry):
        self._entry = entry
        dict.__setitem__(self, 'entry', entry)
        if self._timestamp == 0:
            self._timestamp = time.time()

    def get_entry(self):
        return self._entry

    def set_time(self, time: float):
        self._timestamp = time
        dict.__setitem__(self, 'timestamp', time)

    def get_time(self):
        return self._timestamp

    entry = property(get_entry, set_entry)
    timestamp = property(get_time, set_time)


class DirectMessage(dict):
    """
    Represents a single direct message, stored locally.
    """
    def __init__(self, recipient: str = None, message: str = None,
                 timestamp: float = 0, sender: str = None):
        self.recipient = recipient
        self.message = message
        self.timestamp = timestamp
        self.sender = sender
        dict.__init__(self, recipient=recipient, message=message,
                      timestamp=timestamp, sender=sender)


class Profile:
    """
    The Profile class exposes the properties required to join an
    ICS 32 DSU server.
    Extended for A5 to support direct messages and friends list.
    """

    def __init__(self, dsuserver=None, username=None, password=None):
        self.dsuserver = dsuserver
        self.username = username
        self.password = password
        self.bio = ''
        self._posts = []
        self._friends = []        # list of friend usernames
        self._messages = {}       # {username: [DirectMessage, ...]}

    # -------------------------------------------------------
    # Original Post methods (unchanged)
    # -------------------------------------------------------

    def add_post(self, post: Post) -> None:
        self._posts.append(post)

    def del_post(self, index: int) -> bool:
        try:
            del self._posts[index]
            return True
        except IndexError:
            return False

    def get_posts(self) -> list:
        return self._posts

    # -------------------------------------------------------
    # New A5 methods: Friends
    # -------------------------------------------------------

    def add_friend(self, username: str) -> None:
        """Add a friend username if not already in list."""
        if username not in self._friends:
            self._friends.append(username)

    def get_friends(self) -> list:
        """Return list of friend usernames."""
        return self._friends

    # -------------------------------------------------------
    # New A5 methods: Messages
    # -------------------------------------------------------

    def add_message(self, username: str, message: DirectMessage) -> None:
        """
        Store a message under a username key.
        username = the other person in the conversation.
        """
        if username not in self._messages:
            self._messages[username] = []
        self._messages[username].append({
            'message': message.message,
            'recipient': message.recipient,
            'sender': message.sender,
            'timestamp': message.timestamp
        })

    def get_messages(self, username: str) -> list:
        """
        Return list of messages for a given username.
        Returns empty list if no messages found.
        """
        return self._messages.get(username, [])

    def get_all_messages(self) -> dict:
        """Return entire messages dictionary."""
        return self._messages

    # -------------------------------------------------------
    # Save and Load (extended for friends + messages)
    # -------------------------------------------------------

    def save_profile(self, path: str) -> None:
        """Save profile to a .dsu file."""
        p = Path(path)
        if p.exists() and p.suffix == '.dsu':
            try:
                f = open(p, 'w')
                json.dump(self.__dict__, f)
                f.close()
            except Exception as ex:
                raise DsuFileError(
                    "Error while attempting to process the DSU file.", ex
                )
        else:
            raise DsuFileError("Invalid DSU file path or type")

    def load_profile(self, path: str) -> None:
        """Load profile from a .dsu file."""
        p = Path(path)
        if p.exists() and p.suffix == '.dsu':
            try:
                f = open(p, 'r')
                obj = json.load(f)
                self.username = obj['username']
                self.password = obj['password']
                self.dsuserver = obj['dsuserver']
                self.bio = obj['bio']

                # Load posts
                for post_obj in obj['_posts']:
                    post = Post(post_obj['entry'], post_obj['timestamp'])
                    self._posts.append(post)

                # Load friends (new for A5)
                self._friends = obj.get('_friends', [])

                # Load messages (new for A5)
                self._messages = obj.get('_messages', {})

                f.close()
            except Exception as ex:
                raise DsuProfileError(ex)
        else:
            raise DsuFileError()
