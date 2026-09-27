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

A lightweight **client-server chatroom application built with Python** and designed for learning, experimentation, and understanding basic network communication.

Chatroom provides a simple environment where a server manages connections and clients communicate through it in real time. The project also includes server-side administration commands and a built-in logging system.

> ⚠️ **Project status:** Beta / Educational Project

---

## ✨ Features

* 💬 Real-time client ↔ server messaging
* 🖥️ Dedicated server and client applications
* 🌐 Client connection management
* 🔎 Server-side client IP inspection
* 🚫 Client kicking system
* 🛑 Server shutdown command
* 🧹 Console/text clearing command
* 📝 Automatic server and client logging
* 🇹🇷 Turkish language support
* 🐍 Python-based implementation
* 🔧 Designed with extensibility in mind

---

## 🏗️ Architecture

Chatroom follows a simple **client-server architecture**:

```text
                 ┌─────────────────┐
                 │      SERVER     │
                 │                 │
                 │ Connection Mgmt │
                 │ Logging         │
                 │ Admin Commands  │
                 └────────┬────────┘
                          │
              ┌───────────┼───────────┐
              │           │           │
              ▼           ▼           ▼
          ┌───────┐   ┌───────┐   ┌───────┐
          │Client │   │Client │   │Client │
          │   01  │   │   02  │   │   03  │
          └───────┘   └───────┘   └───────┘
```

The **server** is responsible for establishing and managing connections, while **clients** connect to the server and communicate through it.

---

## 🖥️ Server

The server is the central component of the application.

It is responsible for:

* Accepting client connections
* Managing connected clients
* Handling communication
* Monitoring client IP addresses
* Executing administrative commands
* Recording server-side activity

### Server Commands

| Command      | Description                                   |
| ------------ | --------------------------------------------- |
| `/client_ip` | Displays the IP address of a connected client |
| `/kick`      | Kicks a client from the server                |
| `/shutdown`  | Shuts down the server and closes connections  |
| `/clear`     | Clears the current text/console               |

> **Note:** Some server commands are still under development and may have limitations in the current beta version.

---

## 👤 Client

The client application connects to an active Chatroom server.

Once connected, users can communicate with other connected clients through the server.

The current client focuses primarily on:

* Connecting to the server
* Sending messages
* Receiving messages
* Maintaining a chat session
* Creating client-side logs

---

## 📝 Logging System

Chatroom includes a built-in logging system for both server and client applications.

### Server log

```text
Server_INFO.log
```

### Client log

```text
Client_INFO.log
```

Depending on the application and activity, logs may contain information such as:

* IP addresses
* Connection information
* Messages
* Server activity
* Client activity

### ⚠️ Privacy Notice

Because the application records network and chat activity, **do not use it to collect, distribute, or expose information without the knowledge and consent of the participants.**

If you deploy this project for other users, review the logging behavior and applicable privacy requirements before doing so.

---

## 🛠️ Tech Stack

| Technology           | Purpose                             |
| -------------------- | ----------------------------------- |
| 🐍 Python            | Core application                    |
| 🌐 Socket Networking | Client-server communication         |
| 🎨 Colorama          | Terminal output / formatting        |
| 📝 Logging           | Server and client activity tracking |

---

## 📦 Installation

### 1. Clone the repository

```bash
git clone https://github.com/Kerxunos/Chatroom.git
cd Chatroom
```

### 2. Enter the application directory

```bash
cd Application
```

### 3. Install dependencies

If the project reports a missing Python module, install the required dependency with:

```bash
pip install colorama
```

> A dedicated `requirements.txt` is recommended for future versions so dependencies can be installed with a single command.

---

## ▶️ Running the Application

Start the **server first**.

```bash
python server.py
```

After the server is running, launch the client:

```bash
python client.py
```

The client should then connect to the active server and allow communication with other connected clients.

> The exact filenames or startup commands may change as the project evolves.

---

## 🔐 Security Considerations

Chatroom is primarily an **educational networking project** and should not currently be considered production-ready.

The project currently includes functionality that exposes network information to the server, such as client IP addresses.

Before using the project in a production environment, consider implementing:

* 🔒 Encrypted communication using TLS
* 🔑 Authentication
* 🔐 Secure password handling
* 🛡️ Input validation
* 🚦 Rate limiting
* 🧱 Connection restrictions
* 🧹 Safer log handling
* 🔏 Privacy-conscious logging
* 🛑 Proper client session termination
* 🧪 Automated security testing

**Do not expose the server directly to the public internet without properly reviewing and hardening the networking and security implementation.**

---

## 🗺️ Roadmap

The project is still evolving.

Planned improvements include:

* [ ] 🇬🇧 English language support
* [ ] 🌐 Improved online chat functionality
* [ ] 🛠️ Additional server commands
* [ ] 🐛 Bug fixing and stability improvements
* [ ] 🚫 Improved client kicking system
* [ ] 🔐 Stronger security
* [ ] 📝 Improved logging system
* [ ] 📦 Dependency management with `requirements.txt`
* [ ] 🧪 Automated testing
* [ ] 🖥️ Improved client interface
* [ ] ⚡ Performance improvements
* [ ] 📚 Better documentation

---

## 📁 Project Structure

```text
Chatroom/
│
├── Application/
│   ├── client
│   ├── server
│   └── ...
│
├── LICENSE
└── README.md
```

> The internal structure may change as development continues.

---

## 🎯 Project Goals

Chatroom is more than a simple messaging application.

The main purpose of the project is to provide practical experience with:

* Client-server architecture
* Network programming
* Socket communication
* Connection management
* Logging
* Command-based administration
* Python application development
* Basic network security concepts

The project is intended to evolve as new networking and security concepts are implemented.

---

## ⚠️ Disclaimer

This project is provided for **educational and experimental purposes**.

The developer is not responsible for misuse, unauthorized access, privacy violations, or any damage resulting from the use of this software.

Always obtain appropriate authorization before testing networking or security-related functionality on systems that you do not own or administer.

---

## 📜 License

This project is licensed under the **GNU General Public License v3.0 (GPL-3.0)**.

See the [`LICENSE`](LICENSE) file for the complete license text.

---

## 👨‍💻 Author

**Kerxunos**

GitHub:
https://github.com/Kerxunos

---

<p align="center">
  Made with 🐍 Python
</p>

