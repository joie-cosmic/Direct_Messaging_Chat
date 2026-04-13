# a5.py
#
# ICS 32
# Assignment 5: Direct Messaging Chat
# Author: Joy Zhou
# Email: yunxinz6@uci.edu
# ID number: 32927020
# Description: GUI for direct messaging application
import tkinter as tk
from tkinter import ttk, simpledialog
from ds_messenger import DirectMessenger, DirectMessage
from Profile import Profile, DsuFileError, DsuProfileError
import os


class Body(tk.Frame):
    def __init__(self, root, recipient_selected_callback=None):
        tk.Frame.__init__(self, root)
        self.root = root
        self._contacts = [str]
        self._select_callback = recipient_selected_callback
        self._draw()

    def node_select(self, event):
        index = int(self.posts_tree.selection()[0])
        entry = self._contacts[index]
        if self._select_callback is not None:
            self._select_callback(entry)

    def insert_contact(self, contact: str):
        self._contacts.append(contact)
        id = len(self._contacts) - 1
        self._insert_contact_tree(id, contact)

    def _insert_contact_tree(self, id, contact: str):
        if len(contact) > 25:
            contact = contact[:24] + "..."
        self.posts_tree.insert('', id, id, text=contact)

    def insert_user_message(self, message: str):
        self.entry_editor.configure(state=tk.NORMAL)
        self.entry_editor.insert(tk.END, message + '\n', 'entry-right')
        self.entry_editor.configure(state=tk.DISABLED)

    def insert_contact_message(self, message: str):
        self.entry_editor.configure(state=tk.NORMAL)
        self.entry_editor.insert(tk.END, message + '\n', 'entry-left')
        self.entry_editor.configure(state=tk.DISABLED)

    def get_text_entry(self) -> str:
        return self.message_editor.get('1.0', 'end').rstrip()

    def set_text_entry(self, text: str):
        self.message_editor.delete(1.0, tk.END)
        self.message_editor.insert(1.0, text)

    def clear_messages(self):
        self.entry_editor.configure(state=tk.NORMAL)
        self.entry_editor.delete(1.0, tk.END)
        self.entry_editor.configure(state=tk.DISABLED)

    def _draw(self):
        posts_frame = tk.Frame(master=self, width=250)
        posts_frame.pack(fill=tk.BOTH, side=tk.LEFT)

        self.posts_tree = ttk.Treeview(posts_frame)
        self.posts_tree.bind("<<TreeviewSelect>>", self.node_select)
        self.posts_tree.pack(fill=tk.BOTH, side=tk.TOP,
                             expand=True, padx=5, pady=5)

        entry_frame = tk.Frame(master=self, bg="")
        entry_frame.pack(fill=tk.BOTH, side=tk.TOP, expand=True)

        editor_frame = tk.Frame(master=entry_frame, bg="")
        editor_frame.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)

        scroll_frame = tk.Frame(master=entry_frame, width=10)
        scroll_frame.pack(fill=tk.BOTH, side=tk.LEFT, expand=False)

        message_frame = tk.Frame(master=self)
        message_frame.pack(fill=tk.BOTH, side=tk.TOP, expand=False)

        self.message_editor = tk.Text(message_frame, width=0, height=5)
        self.message_editor.pack(fill=tk.BOTH, side=tk.LEFT,
                                 expand=True, padx=0, pady=0)

        self.entry_editor = tk.Text(editor_frame, width=0, height=5,
                                    state=tk.DISABLED)
        self.entry_editor.tag_configure('entry-right',
                                        justify='right',
                                        foreground='white',
                                        font=('Arial', 14))
        self.entry_editor.tag_configure('entry-left',
                                        justify='left',
                                        foreground='white',
                                        font=('Arial', 14))
        self.entry_editor.pack(fill=tk.BOTH, side=tk.LEFT,
                               expand=True, padx=0, pady=0)

        entry_editor_scrollbar = tk.Scrollbar(
            master=scroll_frame,
            command=self.entry_editor.yview
        )
        self.entry_editor['yscrollcommand'] = entry_editor_scrollbar.set
        entry_editor_scrollbar.pack(fill=tk.Y, side=tk.LEFT,
                                    expand=False, padx=0, pady=0)


class Footer(tk.Frame):
    def __init__(self, root, send_callback=None):
        tk.Frame.__init__(self, root)
        self.root = root
        self._send_callback = send_callback
        self._draw()

    def send_click(self):
        if self._send_callback is not None:
            self._send_callback()

    def set_status(self, message: str):
        self.footer_label.config(text=message)

    def _draw(self):
        save_button = tk.Button(master=self, text="Send",
                                width=20, command=self.send_click)
        save_button.pack(fill=tk.BOTH, side=tk.RIGHT, padx=5, pady=5)

        self.footer_label = tk.Label(master=self, text="Ready.")
        self.footer_label.pack(fill=tk.BOTH, side=tk.LEFT, padx=5)


class NewContactDialog(simpledialog.Dialog):
    def __init__(self, root, title=None, user=None, pwd=None, server=None):
        self.root = root
        self.server = server
        self.user = user
        self.pwd = pwd
        super().__init__(root, title)

    def body(self, frame):
        self.server_label = tk.Label(frame, width=30,
                                     text="DS Server Address")
        self.server_label.pack()
        self.server_entry = tk.Entry(frame, width=30)
        self.server_entry.insert(tk.END, self.server if self.server else '')
        self.server_entry.pack()

        self.username_label = tk.Label(frame, width=30, text="Username")
        self.username_label.pack()
        self.username_entry = tk.Entry(frame, width=30)
        self.username_entry.insert(tk.END, self.user if self.user else '')
        self.username_entry.pack()

        self.password_label = tk.Label(frame, width=30, text="Password")
        self.password_label.pack()
        self.password_entry = tk.Entry(frame, width=30)
        self.password_entry.insert(tk.END, self.pwd if self.pwd else '')
        self.password_entry['show'] = '*'
        self.password_entry.pack()

    def apply(self):
        self.user = self.username_entry.get()
        self.pwd = self.password_entry.get()
        self.server = self.server_entry.get()


class MainApp(tk.Frame):
    def __init__(self, root):
        tk.Frame.__init__(self, root)
        self.root = root
        self.username = None
        self.password = None
        self.server = None
        self.recipient = None
        self.direct_messenger = None
        self.profile = Profile()
        self.profile_path = 'profile.dsu'
        self._draw()
        self._load_profile()

    def _load_profile(self):
        """Load profile from file if exists, restore contacts and messages."""
        if os.path.exists(self.profile_path):
            try:
                self.profile.load_profile(self.profile_path)
                self.username = self.profile.username
                self.password = self.profile.password
                self.server = self.profile.dsuserver

                for friend in self.profile.get_friends():
                    self.body.insert_contact(friend)

                if self.username and self.password and self.server:
                    self.direct_messenger = DirectMessenger(
                        dsuserver=self.server,
                        username=self.username,
                        password=self.password
                    )
                    self.footer.set_status("Connected as " + self.username)
                else:
                    self.footer.set_status(
                        "Ready. Please configure server."
                    )
            except (DsuFileError, DsuProfileError):
                self.footer.set_status("Ready. Please configure server.")
        else:
            self.footer.set_status("Ready. Please configure server.")

    def _save_profile(self):
        """Save current profile to file."""
        try:
            if not os.path.exists(self.profile_path):
                with open(self.profile_path, 'w') as f:
                    pass
            self.profile.save_profile(self.profile_path)
        except DsuFileError as e:
            print(f"Save failed: {e}")

    def send_message(self):
        """Send message to currently selected recipient."""
        if self.recipient is None:
            self.footer.set_status("Please select a contact first!")
            return

        message = self.body.get_text_entry()
        if message == '':
            self.footer.set_status("Please type a message first!")
            return

        if self.direct_messenger is None:
            self.footer.set_status("Please configure server first!")
            return

        success = self.direct_messenger.send(message, self.recipient)

        if success:
            self.body.insert_user_message(f"You: {message}")
            dm = DirectMessage()
            dm.recipient = self.recipient
            dm.message = message
            dm.sender = self.username
            self.profile.add_message(self.recipient, dm)
            self._save_profile()
            self.body.set_text_entry('')
            self.footer.set_status("Message sent!")
        else:
            self.footer.set_status("Failed to send message.")

    def add_contact(self):
        """Add a new contact via dialog."""
        new_contact = simpledialog.askstring(
            "Add Contact", "Enter username to add:"
        )
        if new_contact and new_contact not in self.profile.get_friends():
            self.body.insert_contact(new_contact)
            self.profile.add_friend(new_contact)
            self._save_profile()
            self.footer.set_status(f"Added contact: {new_contact}")

    def recipient_selected(self, recipient):
        """Called when user clicks a contact in the treeview."""
        self.recipient = recipient
        self.body.clear_messages()

        messages = self.profile.get_messages(recipient)
        for msg in messages:
            if msg.get('sender') == self.username:
                self.body.insert_user_message(
                    f"You: {msg.get('message')}"
                )
            else:
                self.body.insert_contact_message(
                    f"{recipient}: {msg.get('message')}"
                )
        self.footer.set_status(f"Chatting with: {recipient}")

    def configure_server(self):
        """Open dialog to configure server settings."""
        ud = NewContactDialog(self.root, "Configure Account",
                              self.username, self.password, self.server)
        self.username = ud.user
        self.password = ud.pwd
        self.server = ud.server

        if self.username and self.password and self.server:
            self.direct_messenger = DirectMessenger(
                dsuserver=self.server,
                username=self.username,
                password=self.password
            )
            self.profile.username = self.username
            self.profile.password = self.password
            self.profile.dsuserver = self.server

            if not os.path.exists(self.profile_path):
                with open(self.profile_path, 'w') as f:
                    pass

            self._save_profile()

            if self.direct_messenger.token:
                self.footer.set_status("Connected as " + self.username)
            else:
                self.footer.set_status("Connection failed!")

    def check_new(self):
        """Auto-check for new messages every 2 seconds."""
        if self.direct_messenger is not None:
            try:
                new_messages = self.direct_messenger.retrieve_new()
                for msg in new_messages:
                    sender = msg.recipient

                    if sender not in self.profile.get_friends():
                        self.body.insert_contact(sender)
                        self.profile.add_friend(sender)

                    dm = DirectMessage()
                    dm.recipient = sender
                    dm.message = msg.message
                    dm.sender = sender
                    self.profile.add_message(sender, dm)

                    if self.recipient == sender:
                        self.body.insert_contact_message(
                            f"{sender}: {msg.message}"
                        )

                if new_messages:
                    self._save_profile()

            except Exception as e:
                print(f"Check new failed: {e}")

        self.root.after(2000, self.check_new)

    def _draw(self):
        menu_bar = tk.Menu(self.root)
        self.root['menu'] = menu_bar

        menu_file = tk.Menu(menu_bar)
        menu_bar.add_cascade(menu=menu_file, label='File')
        menu_file.add_command(label='New')
        menu_file.add_command(label='Open...')
        menu_file.add_command(label='Close')

        settings_file = tk.Menu(menu_bar)
        menu_bar.add_cascade(menu=settings_file, label='Settings')
        settings_file.add_command(label='Add Contact',
                                  command=self.add_contact)
        settings_file.add_command(label='Configure DS Server',
                                  command=self.configure_server)

        self.body = Body(self.root,
                         recipient_selected_callback=self.recipient_selected)
        self.body.pack(fill=tk.BOTH, side=tk.TOP, expand=True)

        self.footer = Footer(self.root, send_callback=self.send_message)
        self.footer.pack(fill=tk.BOTH, side=tk.BOTTOM)


if __name__ == "__main__":
    main = tk.Tk()
    main.title("ICS 32 Distributed Social Messenger")
    main.geometry("720x480")
    main.option_add('*tearOff', False)

    app = MainApp(main)
    app.pack(fill=tk.BOTH, expand=True)

    main.update_idletasks()

    try:
        main.minsize(main.winfo_width(), main.winfo_height())
    except Exception:
        pass

    main.after(2000, app.check_new)

    main.mainloop()
