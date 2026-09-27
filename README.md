# Chatroom 

![License: GPL v3](https://img.shields.io/github/license/Kerxunos/Chatroom)
![Coding](https://img.shields.io/github/languages/top/Kerxunos/Chatroom)
![Size](https://img.shields.io/github/languages/code-size/Kerxunos/Chatroom)
![Colorama](https://img.shields.io/pypi/v/colorama)
![Observatory_Grade](https://img.shields.io/mozilla-observatory/grade/github.com?publish)
![commit_acitivity](https://img.shields.io/github/commit-activity/w/Kerxunos/Chatroom)
![pyapi_format](https://img.shields.io/pypi/format/colorama)
![pymodule_ver](https://img.shields.io/pypi/pyversions/colorama)

![Chatroom2](https://user-images.githubusercontent.com/113096235/195297547-76ce4d07-80ef-4705-a112-24c373ced67b.png)

# 💬 Chatroom

> **A reliable, terminal-based multi-client chat application built with Python sockets.**

Chatroom is a lightweight **client-server terminal chat application** designed to remain usable even on **unstable or limited network connections**.

Unlike a basic socket chat application, Chatroom includes automatic reconnection, application-level heartbeats, message queuing, chat history recovery, rate limiting, private messaging, room moderation and optional password protection.

**Version:** `4.0`
**Language:** Python 3
**License:** GPL-3.0

---

## ✨ Features

### 💬 Real-Time Messaging

* Multi-client TCP communication
* Real-time message broadcasting
* Private messaging
* Action messages
* Username changing
* Online user listing
* Room topics

### 🌐 Connection Reliability

Chatroom was designed with unreliable connections in mind.

* 🔄 Automatic reconnection
* ❤️ Application-level heartbeat
* 🔌 TCP keepalive
* 📦 Outbound message queue
* 🕐 Connection timeout detection
* 📜 Message history recovery after reconnect
* ⏳ Exponential-style reconnect delays

When a connection is temporarily lost, messages typed by the user are **queued instead of being immediately lost**.

Once the connection is restored, queued messages are automatically sent.

### 🛡️ Anti-Spam Protection

The server limits how quickly clients can send messages.

Current limits:

```text
Maximum message length: 1000 characters
Rate limit:              6 messages / 4 seconds
```

This helps prevent a single client from consuming excessive bandwidth or flooding the room.

### 🔐 Password-Protected Rooms

Hosts can optionally protect their rooms with a password.

```bash
python chatroom.py host --port 5000 --username Kerxunos --password 1234
```

Clients can then join using:

```bash
python chatroom.py join --ip 127.0.0.1 --port 5000 --username Ayse --password 1234
```

### 👑 Host Moderation

The host has additional administrative commands:

* `/mute`
* `/unmute`
* `/kick`
* `/topic`
* `/shutdown`

This allows the room owner to manage the conversation without needing a separate administration interface.

### 📝 Logging

Both server and client activity can be logged automatically.

```text
Server_INFO.log
Client_INFO.log
```

Logs are written in append mode so previous sessions are not automatically overwritten.

---

# 🏗️ Architecture

Chatroom uses a traditional **TCP client-server architecture**.

```text
                         ┌─────────────────────┐
                         │       HOST          │
                         │                     │
                         │   ChatServer        │
                         │   TCP Socket        │
                         │   Room Management   │
                         │   Moderation        │
                         │   Message History   │
                         └──────────┬──────────┘
                                    │
                         TCP / JSON │
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
              ▼                     ▼                     ▼
       ┌─────────────┐       ┌─────────────┐       ┌─────────────┐
       │   CLIENT    │       │   CLIENT    │       │   CLIENT    │
       │             │       │             │       │             │
       │ ChatClient  │       │ ChatClient  │       │ ChatClient  │
       │ Auto-Reconn │       │ Message Q.  │       │ Heartbeat   │
       └─────────────┘       └─────────────┘       └─────────────┘
```

The server maintains connected clients and broadcasts messages.

Clients communicate with the server through a lightweight **JSON-over-TCP protocol**.

---

# 🔌 Communication Protocol

Chatroom uses a simple line-based protocol.

Each message is encoded as:

```text
JSON + newline
```

For example:

```json
{
  "type": "chat",
  "text": "Hello everyone!"
}
```

The newline delimiter allows the receiver to correctly separate multiple messages arriving in a single TCP `recv()` call.

This is handled by the internal `LineReceiver` class.

### Supported message types include

```text
hello
welcome
chat
action
whisper
whisper_sent
heartbeat
heartbeat_ack
ping
pong
nick
nick_ack
list_request
userlist
topic
kick
shutdown
bye
system
```

---

# 🔄 Connection Recovery

One of the main goals of Chatroom is surviving temporary network failures.

### Automatic Reconnection

When a client loses its connection, it automatically attempts to reconnect using progressively longer delays:

```text
1s
2s
5s
10s
15s
30s
...
```

Once a connection is successfully restored, the retry counter resets.

---

## 📦 Message Queue

Messages written while disconnected are placed into an outbound queue.

```text
User types message
       │
       ▼
Connection available?
   ┌───┴───┐
  YES      NO
   │        │
   ▼        ▼
 Send     Queue
            │
            ▼
       Reconnection
            │
            ▼
      Send queued
       messages
```

This prevents messages from simply disappearing when the network temporarily goes down.

---

# ❤️ Heartbeat System

Chatroom uses two levels of connection monitoring.

### TCP Keepalive

Sockets are configured with TCP keepalive where supported by the operating system.

### Application Heartbeat

The client periodically sends:

```json
{
  "type": "heartbeat"
}
```

The server responds with:

```json
{
  "type": "heartbeat_ack"
}
```

This allows the application to detect connections that appear open at the TCP level but are no longer actually usable.

---

# 📜 Message History

The server keeps a configurable amount of recent chat history.

Default:

```text
30 messages
```

When a client reconnects, the server sends the stored history along with the welcome packet.

The client then displays:

```text
--- kaçırdığınız mesajlar ---
[geçmiş] [14:21] Kerem: Merhaba
[geçmiş] [14:21] Ayşe: Selam!
[geçmiş] [14:22] Kerem: Nasılsınız?
--- geçmiş sonu ---
```

The history is intentionally limited rather than being a permanent database.

---

# 👥 Multi-Client Support

The server supports multiple simultaneous clients.

The default maximum is:

```text
25 clients
```

This can be changed when starting the server:

```bash
python chatroom.py host \
    --port 5000 \
    --username Kerxunos \
    --max-clients 50
```

---

# 💻 Installation

## Requirements

* Python **3.10+**
* TCP/IP network connectivity
* `colorama`

Python's standard library provides the rest of the functionality.

### Install dependency

```bash
pip install colorama
```

Or:

```bash
python -m pip install colorama
```

---

# 🚀 Quick Start

## 1. Clone the repository

```bash
git clone https://github.com/Kerxunos/Chatroom.git
cd Chatroom
```

## 2. Start a server

```bash
python chatroom.py host --port 5000 --username Kerxunos
```

You should see something similar to:

```text
[*] Oda açıldı -> 0.0.0.0:5000
```

## 3. Connect a client

On another terminal or another computer:

```bash
python chatroom.py join \
    --ip 127.0.0.1 \
    --port 5000 \
    --username Ayse
```

You can now start chatting.

---

# 🔐 Password-Protected Room

### Host

```bash
python chatroom.py host \
    --port 5000 \
    --username Kerxunos \
    --password 1234
```

### Client

```bash
python chatroom.py join \
    --ip 127.0.0.1 \
    --port 5000 \
    --username Ayse \
    --password 1234
```

If the password is incorrect, the server rejects the connection.

---

# 🖥️ Interactive Mode

You don't have to provide all arguments manually.

Running:

```bash
python chatroom.py
```

starts an interactive setup.

You can choose:

```text
Oda mı açacaksınız yoksa bir odaya mı katılacaksınız?
[H]ost / [J]oin:
```

The application then asks for the required information.

---

# ⌨️ Commands

## 👤 General Commands

Available to everyone:

| Command                 | Description             |
| ----------------------- | ----------------------- |
| `/help`                 | Show available commands |
| `/users`                | List connected users    |
| `/list`                 | Alias for `/users`      |
| `/nick <name>`          | Change username         |
| `/msg <user> <message>` | Send private message    |
| `/w <user> <message>`   | Alias for `/msg`        |
| `/me <action>`          | Send an action message  |
| `/clear`                | Clear your terminal     |

### Example

```text
/msg Ayse Merhaba, özelden konuşalım.
```

Output:

```text
(fısıltı -> Ayse): Merhaba, özelden konuşalım.
```

---

## 👤 Client Commands

| Command | Description                |
| ------- | -------------------------- |
| `/ping` | Measure round-trip latency |
| `/quit` | Leave the room             |
| `/exit` | Alias for `/quit`          |

Example:

```text
/ping
```

Output:

```text
[*] Ping: 24 ms
```

---

# 👑 Host Commands

The room owner has additional controls.

| Command                 | Description                          |
| ----------------------- | ------------------------------------ |
| `/mute <user>`          | Prevent a user from sending messages |
| `/unmute <user>`        | Remove mute                          |
| `/topic`                | Show current room topic              |
| `/topic <text>`         | Change room topic                    |
| `/kick <user>`          | Remove a user                        |
| `/kick <user> <reason>` | Remove a user with a reason          |
| `/shutdown`             | Close the room                       |

### Example

```text
/topic Computer Engineering Room
```

Or:

```text
/kick Ayse Spam yapıldığı için
```

---

# ⚙️ Configuration

Several important limits can be configured directly in the source code.

```python
MAX_MESSAGE_LEN = 1000
RATE_LIMIT_COUNT = 6
RATE_LIMIT_WINDOW = 4.0
DEFAULT_HISTORY_SIZE = 30
DEFAULT_MAX_CLIENTS = 25
SOCKET_POLL_TIMEOUT = 15
HEARTBEAT_INTERVAL = 20
IDLE_DISCONNECT_AFTER = 55
RECONNECT_DELAYS = [1, 2, 5, 10, 15, 30]
```

### Current defaults

| Setting                |                 Default |
| ---------------------- | ----------------------: |
| Maximum message length |         1000 characters |
| Rate limit             |      6 messages / 4 sec |
| Message history        |             30 messages |
| Maximum clients        |                      25 |
| Socket poll timeout    |                  15 sec |
| Heartbeat interval     |                  20 sec |
| Idle disconnect        |                  55 sec |
| Reconnect delays       | 1, 2, 5, 10, 15, 30 sec |

---

# 🗂️ Logging

The application creates separate log files for server and client activity.

```text
Server_INFO.log
Client_INFO.log
```

Example entries:

```text
2026-09-27 14:20:12 - Server started on 0.0.0.0:5000 as Kerxunos
2026-09-27 14:21:04 - Ayse connected from 192.168.1.25:53142
2026-09-27 14:21:18 - Ayse: Hello everyone!
```

Logging uses Python's built-in `logging` module.

---

# 🛡️ Security Considerations

Chatroom includes several basic protections:

* Maximum message length
* Rate limiting
* Optional room password
* Connection timeout handling
* Maximum client limit
* Host moderation
* TCP keepalive
* Input validation for usernames
* Limited message history

However, **Chatroom is not currently intended to be a production-grade secure messaging system.**

## Important limitations

The current protocol uses plain TCP with JSON messages.

There is currently no:

* TLS encryption
* End-to-end encryption
* User account system
* Persistent authentication
* Password hashing
* Database-backed user management

Therefore, sensitive information should **not** be transmitted through the application in its current form.

If the project is deployed outside a trusted local network, additional security mechanisms should be implemented.

---

# 🧠 Technical Highlights

This project was built to explore several practical networking concepts rather than simply implementing a basic chat socket.

### Python Networking

```python
socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)
```

The application uses TCP sockets for reliable transport.

### Concurrency

The server creates a dedicated daemon thread for each client connection:

```python
threading.Thread(
    target=self._handle_client,
    args=(conn, addr),
    daemon=True
)
```

This allows multiple clients to communicate concurrently.

### Thread Safety

Shared server state is protected using:

```python
threading.RLock()
```

This is particularly important for:

* Client lists
* Message broadcasting
* Username management
* Connection handling

### Queue-Based Delivery

The client uses:

```python
queue.Queue()
```

to temporarily store outbound messages while disconnected.

### Efficient History Storage

Recent messages are stored using:

```python
collections.deque
```

with a configurable maximum size.

This prevents the history from growing indefinitely.

---

# 📁 Project Structure

The application is intentionally kept lightweight and currently centers around a single Python entry point:

```text
Chatroom/
│
├── chatroom.py
├── LICENSE
├── README.md
│
├── Server_INFO.log      # generated at runtime
└── Client_INFO.log      # generated at runtime
```

Runtime log files are generated automatically and are not part of the core source code.

---

# 🧪 Example Session

### Host

```text
$ python chatroom.py host --port 5000 --username Kerxunos

[*] Oda açıldı -> 0.0.0.0:5000
Komutlar için /help yazın.
```

### Client

```text
$ python chatroom.py join \
    --ip 192.168.1.10 \
    --port 5000 \
    --username Ayse

[*] 192.168.1.10:5000 adresine bağlanılıyor...
[*] Odaya bağlanıldı! Host: Kerxunos
```

### Chat

```text
Ayse--> Merhaba!

[14:32] Ayse: Merhaba!
[14:32] Kerxunos: Hoş geldin!
```

### Temporary connection loss

```text
[!] Sunucudan uzun süredir yanıt yok,
bağlantı yeniden kuruluyor...

[*] 1 saniye sonra yeniden bağlanılacak (deneme 1)...

[*] Odaya bağlanıldı! Host: Kerxunos
--- kaçırdığınız mesajlar ---
[geçmiş] [14:33] Kerxunos: Tekrar bağlandın mı?
--- geçmiş sonu ---
```

---

# 🗺️ Roadmap

Possible future improvements:

* [ ] 🔐 TLS encryption
* [ ] 🔑 Secure authentication
* [ ] 🗄️ Persistent message storage
* [ ] 🧪 Automated unit and integration tests
* [ ] 📊 Better connection statistics
* [ ] 🖥️ Improved terminal UI
* [ ] 🌍 English language support
* [ ] 🔒 Password hashing
* [ ] 🛡️ More robust input validation
* [ ] 📦 Dependency management with `requirements.txt`
* [ ] 🐳 Docker support
* [ ] ⚡ Performance improvements
* [ ] 📚 Protocol documentation
* [ ] 🔄 More advanced reconnect/session handling

---

# 🤝 Contributing

Contributions, ideas and bug reports are welcome.

If you find a bug or have an idea for improving Chatroom:

1. Fork the repository.
2. Create a feature branch.

```bash
git checkout -b feature/my-feature
```

3. Commit your changes.

```bash
git commit -m "Add my feature"
```

4. Push the branch.

```bash
git push origin feature/my-feature
```

5. Open a Pull Request.

---

# ⚠️ Disclaimer

Chatroom is primarily an **educational and experimental networking project**.

Do not use it to intercept, monitor, or collect network traffic or personal information without proper authorization.

The developer is not responsible for misuse of the software.

---

# 📜 License

This project is licensed under the **GNU General Public License v3.0**.

See [`LICENSE`](LICENSE) for the complete license text.

---

# 👨‍💻 Author

## Kerxunos

Python developer interested in:

* 🐍 Python
* 🌐 Network Programming
* 🔐 Cybersecurity
* 🖥️ Software Development
* ☁️ Cloud Technologies

GitHub: **[github.com/Kerxunos](https://github.com/Kerxunos)**

---

<p align="center">

### 💬 Chatroom

**Simple interface. Reliable communication. Built with Python.**

Made with 🐍 and ☕ by **Kerxunos**

</p>

