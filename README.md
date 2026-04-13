Direct Messaging Chat - ICS department
============================================

Description
-----------
This program is a direct messaging application built using Python and Tkinter.
It allows users to send and receive direct messages through the ICS 32
Distributed Social Platform (DSP) server. Users can add contacts, send messages,
and view message history. The application automatically retrieves new messages
every 2 seconds without requiring manual refresh.

Files
-----
a5.py
    Main program file containing the Tkinter GUI implementation.
    Run this file to start the application.

ds_messenger.py
    Contains the DirectMessenger and DirectMessage classes.
    Handles all communication with the DSP server including
    sending and retrieving messages.

ds_protocol.py
    Contains protocol functions for packaging and parsing
    JSON messages according to the DSP server requirements.

Profile.py
    Manages user profile data including authentication credentials,
    friends list, and message history. Data is stored locally
    in a .dsu file.

test_ds_message_protocol.py
    Unit tests for the ds_protocol module.

test_ds_messenger.py
    Unit tests for the ds_messenger module.

How to Run
----------
python3 a5.py

Then:
1. Click Settings -> Configure DS Server
2. Enter server address, username, and password
3. Click Settings -> Add Contact to add a recipient
4. Select a contact and type a message
5. Click Send


Note: The server at ics32.clotho.ics.uci.edu is only accessible 
from the UCI campus network. If you are off-campus, you must 
connect to the UCI VPN before running this program.

