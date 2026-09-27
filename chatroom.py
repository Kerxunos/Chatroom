#!/usr/bin/env python3
"""
Chatroom - Tek dosyalık, kısıtlı/kararsız internet bağlantılarında bile
güvenilir şekilde çalışan, çok istemcili terminal sohbet uygulaması.
==========================================================================

Bu sürüm; bağlantı kopmalarına karşı otomatik yeniden bağlanma, TCP
seviyesinde ve uygulama seviyesinde "heartbeat" (canlılık yoklaması),
bağlantı koptuğunda yazılan mesajları kaybetmeyen bir gönderim kuyruğu,
yeniden bağlanan kullanıcı için kısa mesaj geçmişi tekrarı, mesaj boyu
sınırlaması ve hız sınırlaması (spam koruması) gibi "gerçek hayatta işe
yarayan" özellikler içerir.

Kullanım
--------
Oda açmak (host):
    python chatroom.py host --bind 0.0.0.0 --port 5000 --username Kerem
    python chatroom.py host --port 5000 --username Kerem --password 1234

Bir odaya katılmak (join):
    python chatroom.py join --ip 127.0.0.1 --port 5000 --username Ayse
    python chatroom.py join --ip 1.2.3.4 --port 5000 --username Ayse --password 1234

Argümansız çalıştırırsanız program sizi interaktif olarak yönlendirir.

Komutlar (herkes):
    /help                     komut listesini gösterir
    /users  (/list)           odadaki kullanıcıları listeler
    /nick <yeni_ad>           kullanıcı adınızı değiştirir
    /msg <kullanici> <mesaj>  (/w) özel mesaj gönderir
    /me <eylem>               aksiyon mesajı yazar  (* Kerem kahve içiyor)
    /clear                    yalnızca kendi ekranınızı temizler
    /quit  (/exit)            sohbetten ayrılır  (yalnızca istemci)

İstemciye özel:
    /ping                     sunucuya olan gecikmeyi (ms) gösterir

Host'a (oda sahibi) özel:
    /mute <kullanici>         kullanıcıyı susturur
    /unmute <kullanici>       susturmayı kaldırır
    /topic [yeni_konu]        oda konusunu gösterir / değiştirir
    /kick <kullanici> [sebep] kullanıcıyı odadan atar
    /shutdown                 odayı kapatır, herkesin bağlantısını keser

Dayanıklılık özellikleri
-------------------------
* İstemci bağlantısı koparsa otomatik olarak, artan bekleme süreleriyle
  (1s, 2s, 5s, 10s, 15s, 30s...) yeniden bağlanmayı dener.
* Bağlantı kopukken yazılan mesajlar kaybolmaz; bir kuyruğa alınır ve
  bağlantı geri geldiğinde otomatik olarak gönderilir.
* Uygulama seviyesinde "heartbeat" sayesinde, TCP'nin fark etmesi uzun
  sürebilecek "sessizce ölmüş" bağlantılar hızlıca tespit edilir.
* Yeniden bağlanan bir kullanıcıya, kaçırdığı son mesajlar (kısa bir
  geçmiş penceresi) otomatik olarak tekrar gösterilir.
* Mesaj uzunluğu ve gönderim hızı sınırlandırılarak, kısıtlı bant
  genişliğinin birkaç kişi tarafından tüketilmesi engellenir.

Loglama
-------
Sunucu "Server_INFO.log", istemci ise "Client_INFO.log" dosyasına
(üzerine yazmadan, ekleyerek) log tutar.

Lisans: GPL-3.0 (bkz. LICENSE)
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import queue
import socket
import sys
import threading
import time
from collections import deque
from dataclasses import dataclass, field

try:
    from colorama import Fore, Style, init as _colorama_init
    _colorama_init(autoreset=True)
    _COLOR_AVAILABLE = True
except ImportError:  # colorama kurulu değilse renksiz çalışmaya devam et
    class _NoColor:
        def __getattr__(self, _name):
            return ""

    Fore = _NoColor()
    Style = _NoColor()
    _COLOR_AVAILABLE = False

APP_VERSION = "4.0"
BANNER = r"""
   ______           __                                
  / ____/  ____ _  / /_    _____  ____   ____   ____ ___
 / /      / __ `/ / __ \  / ___/ / __ \ / __ \ / __ `__ \
/ /___   / /_/ / / /_/ / / /    / /_/ // /_/ // / / / / /
\____/   \__,_/ /_.___/ /_/     \____/ \____//_/ /_/ /_/
        by @Kerxunos                         v{version}
""".format(version=APP_VERSION)

# -- ayarlanabilir sabitler --------------------------------------------------
MAX_MESSAGE_LEN = 1000          # tek bir mesajda izin verilen azami karakter
RATE_LIMIT_COUNT = 6            # RATE_LIMIT_WINDOW saniyede izin verilen mesaj sayısı
RATE_LIMIT_WINDOW = 4.0
DEFAULT_HISTORY_SIZE = 30       # yeniden katılan kullanıcıya tekrar gösterilecek mesaj sayısı
DEFAULT_MAX_CLIENTS = 25
SOCKET_POLL_TIMEOUT = 15        # recv() bu sürede timeout olur, döngü canlı kalır
HEARTBEAT_INTERVAL = 20         # bu kadar süre sessiz kalınırsa heartbeat gönderilir
IDLE_DISCONNECT_AFTER = 55      # bu kadar süre hiç veri gelmezse bağlantı ölü sayılır
RECONNECT_DELAYS = [1, 2, 5, 10, 15, 30]


# ---------------------------------------------------------------------------
# Yardımcı fonksiyonlar
# ---------------------------------------------------------------------------

def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def setup_logging(logger_name: str, filename: str) -> logging.Logger:
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.FileHandler(filename, mode="a", encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
        logger.addHandler(handler)
    return logger


def hhmm(ts: float | None = None) -> str:
    return time.strftime("%H:%M", time.localtime(ts if ts is not None else time.time()))


def send_json(sock: socket.socket, payload: dict, lock: threading.RLock | None = None) -> None:
    """Bir mesajı JSON + newline olarak gönderir (satır tabanlı protokol)."""
    data = (json.dumps(payload, ensure_ascii=False) + "\n").encode("utf-8")
    if lock:
        with lock:
            sock.sendall(data)
    else:
        sock.sendall(data)


def enable_tcp_keepalive(sock: socket.socket) -> None:
    """En iyi çaba (best-effort) TCP keepalive ayarları; platforma göre değişebilir."""
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    except OSError:
        return
    for opt_name, value in (("TCP_KEEPIDLE", 30), ("TCP_KEEPINTVL", 10), ("TCP_KEEPCNT", 4)):
        opt = getattr(socket, opt_name, None)
        if opt is not None:
            try:
                sock.setsockopt(socket.IPPROTO_TCP, opt, value)
            except OSError:
                pass


class LineReceiver:
    """Soketten gelen baytları biriktirip tam JSON satırları döndürür.

    TCP akış tabanlı olduğu için tek bir recv() çağrısı bir mesajın
    tamamını ya da birden fazla mesajı içerebilir; bu sınıf o sorunu
    ortadan kaldırır. Ayrıca periyodik recv() zaman aşımlarında
    {"type": "__timeout__"} üretir; böylece çağıran taraf heartbeat
    gönderip bağlantının hâlâ canlı olup olmadığını kontrol edebilir.
    """

    def __init__(self, sock: socket.socket, timeout: float | None = SOCKET_POLL_TIMEOUT):
        self.sock = sock
        self.buffer = b""
        if timeout:
            sock.settimeout(timeout)

    def messages(self):
        while True:
            try:
                chunk = self.sock.recv(4096)
            except socket.timeout:
                yield {"type": "__timeout__"}
                continue
            except OSError:
                return
            if not chunk:
                return
            self.buffer += chunk
            while b"\n" in self.buffer:
                line, self.buffer = self.buffer.split(b"\n", 1)
                if not line.strip():
                    continue
                try:
                    yield json.loads(line.decode("utf-8"))
                except json.JSONDecodeError:
                    continue


HELP_COMMON = """Komutlar:
  /help                    bu listeyi gösterir
  /users veya /list        odadaki kullanıcıları listeler
  /nick <yeni_ad>          kullanıcı adınızı değiştirir
  /msg <kullanici> <metin> (/w) özel mesaj gönderir
  /me <eylem>              aksiyon mesajı yazar
  /clear                   yalnızca kendi ekranınızı temizler"""

HELP_CLIENT_EXTRA = """  /ping                    sunucuya olan gecikmeyi gösterir
  /quit veya /exit         sohbetten ayrılır"""

HELP_HOST_EXTRA = """  /mute <kullanici>        kullanıcıyı susturur
  /unmute <kullanici>      susturmayı kaldırır
  /topic [yeni_konu]       oda konusunu gösterir / değiştirir
  /kick <kullanici> [sebep] kullanıcıyı odadan atar
  /shutdown                odayı kapatır"""


# ---------------------------------------------------------------------------
# SUNUCU
# ---------------------------------------------------------------------------

@dataclass
class ClientInfo:
    username: str
    addr: tuple
    last_activity: float = field(default_factory=time.time)
    msg_times: deque = field(default_factory=lambda: deque(maxlen=RATE_LIMIT_COUNT))
    muted: bool = False


class ChatServer:
    def __init__(self, bind_ip: str, port: int, username: str, password: str | None,
                 max_clients: int = DEFAULT_MAX_CLIENTS, history_size: int = DEFAULT_HISTORY_SIZE):
        self.bind_ip = bind_ip
        self.port = port
        self.username = username
        self.password = password or None
        self.max_clients = max_clients
        self.topic = ""
        self.server_sock: socket.socket | None = None
        self.clients: dict[socket.socket, ClientInfo] = {}
        self.history: deque = deque(maxlen=history_size)
        self.lock = threading.RLock()
        self.running = True
        self.logger = setup_logging("server", "Server_INFO.log")

    # -- yardımcılar -----------------------------------------------------
    def _usernames(self) -> set[str]:
        return {info.username for info in self.clients.values()}

    def _find_conn(self, username: str) -> socket.socket | None:
        for conn, info in self.clients.items():
            if info.username == username:
                return conn
        return None

    def _remember(self, payload: dict) -> None:
        """Sohbet/aksiyon/sistem mesajlarını kısa geçmişte tutar (fısıltılar hariç)."""
        if payload.get("type") in ("chat", "action", "system"):
            self.history.append(payload)

    # -- genel yayın --------------------------------------------------
    def broadcast(self, payload: dict, exclude: socket.socket | None = None, remember: bool = True) -> None:
        payload.setdefault("ts", time.time())
        if remember:
            self._remember(payload)
        with self.lock:
            dead = []
            for conn in self.clients:
                if conn is exclude:
                    continue
                try:
                    send_json(conn, payload)
                except OSError:
                    dead.append(conn)
            for conn in dead:
                self._drop_client(conn, announce=True, reason="bağlantı hatası")

    def _send_to(self, conn: socket.socket, payload: dict) -> bool:
        payload.setdefault("ts", time.time())
        try:
            send_json(conn, payload)
            return True
        except OSError:
            return False

    def _drop_client(self, conn: socket.socket, announce: bool, reason: str = "") -> None:
        info = self.clients.pop(conn, None)
        try:
            conn.close()
        except OSError:
            pass
        if info and announce:
            suffix = f" ({reason})" if reason else ""
            print(Fore.YELLOW + f"[*] {info.username} bağlantıyı kapattı{suffix}.")
            self.logger.info(f"{info.username} disconnected{suffix}")

    # -- istemci kabul döngüsü ----------------------------------------
    def accept_loop(self) -> None:
        while self.running:
            try:
                conn, addr = self.server_sock.accept()
            except OSError:
                return
            enable_tcp_keepalive(conn)
            threading.Thread(target=self._handle_client, args=(conn, addr), daemon=True).start()

    def _handle_client(self, conn: socket.socket, addr) -> None:
        receiver = LineReceiver(conn, timeout=SOCKET_POLL_TIMEOUT)
        gen = receiver.messages()

        # ilk mesaj "hello" olmalı; zaman aşımlarını atlayarak bekle
        first = None
        for msg in gen:
            if msg.get("type") == "__timeout__":
                continue
            first = msg
            break
        if not first or first.get("type") != "hello":
            conn.close()
            return

        cli_username = str(first.get("username", "")).strip()[:32]
        cli_password = first.get("password")

        if not cli_username:
            self._send_to(conn, {"type": "reject", "reason": "invalid_username"})
            conn.close()
            return
        if self.password and cli_password != self.password:
            self._send_to(conn, {"type": "reject", "reason": "invalid_password"})
            conn.close()
            return
        with self.lock:
            if len(self.clients) >= self.max_clients:
                self._send_to(conn, {"type": "reject", "reason": "room_full"})
                conn.close()
                return
            if cli_username in self._usernames():
                cli_username = f"{cli_username}_{addr[1]}"
            self.clients[conn] = ClientInfo(username=cli_username, addr=addr)

        self._send_to(conn, {
            "type": "welcome",
            "username": self.username,
            "topic": self.topic,
            "history": list(self.history),
        })
        print(Fore.GREEN + f"[*] {cli_username} ({addr[0]}) odaya katıldı.")
        self.logger.info(f"{cli_username} connected from {addr[0]}:{addr[1]}")
        self.broadcast({"type": "system", "text": f"{cli_username} odaya katıldı."}, exclude=conn)

        for msg in gen:
            mtype = msg.get("type")
            with self.lock:
                info = self.clients.get(conn)
            if not info:
                break
            info.last_activity = time.time()

            if mtype == "__timeout__":
                if time.time() - info.last_activity > IDLE_DISCONNECT_AFTER:
                    self._drop_client(conn, announce=True, reason="zaman aşımı")
                    self.broadcast({"type": "system", "text": f"{info.username} zaman aşımına uğradı."})
                    return
                continue

            if mtype == "heartbeat":
                self._send_to(conn, {"type": "heartbeat_ack"})
                continue

            if mtype == "ping":
                self._send_to(conn, {"type": "pong", "echo_ts": msg.get("ts")})
                continue

            if mtype == "bye":
                break

            if mtype in ("chat", "action"):
                # hız sınırlaması: RATE_LIMIT_WINDOW içinde RATE_LIMIT_COUNT'tan
                # fazla mesaj gönderen kullanıcının fazlalık mesajları reddedilir
                now = time.time()
                info.msg_times.append(now)
                if len(info.msg_times) == info.msg_times.maxlen and now - info.msg_times[0] < RATE_LIMIT_WINDOW:
                    self._send_to(conn, {"type": "system", "text": "Çok hızlı mesaj gönderiyorsunuz, lütfen yavaşlayın."})
                    continue
                text = str(msg.get("text", ""))
                if len(text) > MAX_MESSAGE_LEN:
                    self._send_to(conn, {"type": "system",
                                          "text": f"Mesajınız çok uzun (azami {MAX_MESSAGE_LEN} karakter), gönderilmedi."})
                    continue
                if info.muted:
                    self._send_to(conn, {"type": "system", "text": "Susturuldunuz, mesajlarınız diğer kullanıcılara iletilmiyor."})
                    continue
                print(f"{info.username}: {text}" if mtype == "chat" else f"* {info.username} {text}")
                self.logger.info(f"{info.username}: {text}" if mtype == "chat" else f"* {info.username} {text}")
                self.broadcast({"type": mtype, "from": info.username, "text": text}, exclude=conn)

            elif mtype == "whisper":
                target_name = str(msg.get("to", ""))
                text = str(msg.get("text", ""))[:MAX_MESSAGE_LEN]
                if target_name == self.username:
                    # hedef host'un kendisi: doğrudan host konsoluna yaz
                    print(Fore.MAGENTA + f"(fısıltı) {info.username}: {text}")
                    self.logger.info(f"{info.username} -> {self.username} (whisper): {text}")
                    self._send_to(conn, {"type": "whisper_sent", "to": target_name, "text": text})
                    continue
                target_conn = self._find_conn(target_name)
                if not target_conn:
                    self._send_to(conn, {"type": "system", "text": f"Kullanıcı bulunamadı: {target_name}"})
                else:
                    self._send_to(target_conn, {"type": "whisper", "from": info.username, "text": text})
                    self._send_to(conn, {"type": "whisper_sent", "to": target_name, "text": text})
                    self.logger.info(f"{info.username} -> {target_name} (whisper): {text}")

            elif mtype == "nick":
                new_name = str(msg.get("new", "")).strip()[:32]
                with self.lock:
                    taken = new_name in self._usernames()
                if not new_name or taken:
                    self._send_to(conn, {"type": "system", "text": "Bu kullanıcı adı geçersiz veya kullanımda."})
                else:
                    old_name = info.username
                    info.username = new_name
                    self._send_to(conn, {"type": "nick_ack", "username": new_name})
                    self.broadcast({"type": "system", "text": f"{old_name} artık {new_name} olarak biliniyor."})
                    self.logger.info(f"{old_name} renamed to {new_name}")

            elif mtype == "list_request":
                with self.lock:
                    names = sorted([self.username] + [i.username for i in self.clients.values()])
                self._send_to(conn, {"type": "userlist", "users": names})

        self._drop_client(conn, announce=False)
        self.broadcast({"type": "system", "text": f"{info.username if info else cli_username} odadan ayrıldı."})

    # -- host komutları -------------------------------------------------
    def _list_users(self) -> None:
        with self.lock:
            others = sorted(info.username for info in self.clients.values())
        if not others:
            print(Fore.YELLOW + "[*] Odada sizden başka kimse yok.")
        else:
            print(Fore.CYAN + "[*] Odadakiler: " + ", ".join([self.username] + others))

    def _kick_user(self, arg: str) -> None:
        parts = arg.split(" ", 1)
        target = parts[0].strip()
        reason = parts[1].strip() if len(parts) > 1 else ""
        conn = self._find_conn(target)
        if not conn:
            print(Fore.RED + f"[!] '{target}' bulunamadı.")
            return
        self._send_to(conn, {"type": "kick", "reason": reason})
        self._drop_client(conn, announce=False)
        suffix = f" (sebep: {reason})" if reason else ""
        print(Fore.YELLOW + f"[*] {target} odadan atıldı{suffix}.")
        self.logger.info(f"{target} kicked by host{suffix}")
        self.broadcast({"type": "system", "text": f"{target} odadan atıldı{suffix}."})

    def _mute_user(self, target: str, muted: bool) -> None:
        with self.lock:
            info = next((i for i in self.clients.values() if i.username == target), None)
        if not info:
            print(Fore.RED + f"[!] '{target}' bulunamadı.")
            return
        info.muted = muted
        verb = "susturuldu" if muted else "susturması kaldırıldı"
        print(Fore.YELLOW + f"[*] {target} {verb}.")
        self.logger.info(f"{target} {verb} by host")

    def _set_topic(self, new_topic: str) -> None:
        if not new_topic:
            print(Fore.CYAN + f"[*] Oda konusu: {self.topic or '(belirtilmemiş)'}")
            return
        self.topic = new_topic
        print(Fore.GREEN + f"[*] Oda konusu güncellendi: {new_topic}")
        self.broadcast({"type": "topic", "text": new_topic})

    def shutdown(self) -> None:
        self.running = False
        self.broadcast({"type": "shutdown"}, remember=False)
        with self.lock:
            for conn in list(self.clients):
                self._drop_client(conn, announce=False)
        try:
            self.server_sock.close()
        except OSError:
            pass

    def _dispatch_command(self, msg: str) -> bool:
        """Host komutunu işler. Komut değilse False döner."""
        if msg == "/help":
            print(HELP_COMMON)
            print(HELP_HOST_EXTRA)
        elif msg in ("/users", "/list"):
            self._list_users()
        elif msg.startswith("/nick "):
            new_name = msg.split(" ", 1)[1].strip()[:32]
            if new_name and new_name not in self._usernames():
                old = self.username
                self.username = new_name
                print(Fore.GREEN + f"[*] Kullanıcı adınız artık: {new_name}")
                self.broadcast({"type": "system", "text": f"{old} artık {new_name} olarak biliniyor."})
            else:
                print(Fore.RED + "[!] Geçersiz veya kullanımda olan bir isim.")
        elif msg.startswith("/msg ") or msg.startswith("/w "):
            _, rest = msg.split(" ", 1)
            if " " not in rest:
                print(Fore.RED + "[!] Kullanım: /msg <kullanici> <mesaj>")
            else:
                target, text = rest.split(" ", 1)
                conn = self._find_conn(target)
                if not conn:
                    print(Fore.RED + f"[!] '{target}' bulunamadı.")
                else:
                    self._send_to(conn, {"type": "whisper", "from": self.username, "text": text})
                    print(Fore.MAGENTA + f"(fısıltı -> {target}): {text}")
                    self.logger.info(f"{self.username} -> {target} (whisper): {text}")
        elif msg.startswith("/me "):
            action = msg.split(" ", 1)[1]
            print(Fore.CYAN + f"* {self.username} {action}")
            self.logger.info(f"* {self.username} {action}")
            self.broadcast({"type": "action", "from": self.username, "text": action})
        elif msg.startswith("/topic"):
            new_topic = msg[len("/topic"):].strip()
            self._set_topic(new_topic)
        elif msg.startswith("/mute "):
            self._mute_user(msg.split(" ", 1)[1].strip(), True)
        elif msg.startswith("/unmute "):
            self._mute_user(msg.split(" ", 1)[1].strip(), False)
        elif msg.startswith("/kick "):
            self._kick_user(msg.split(" ", 1)[1].strip())
        elif msg == "/clear":
            clear_screen()
        else:
            return False
        return True

    # -- ana çalışma noktası --------------------------------------------
    def run(self) -> None:
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_sock.bind((self.bind_ip, self.port))
        self.server_sock.listen(8)
        print(Fore.GREEN + f"[*] Oda açıldı -> {self.bind_ip}:{self.port} (kullanıcı: {self.username})")
        if self.password:
            print(Fore.YELLOW + "[*] Oda şifre ile korunuyor.")
        self.logger.info(f"Server started on {self.bind_ip}:{self.port} as {self.username}")
        print("Komutlar için /help yazın. Çıkmak için /shutdown veya Ctrl+C.")

        threading.Thread(target=self.accept_loop, daemon=True).start()

        try:
            while self.running:
                try:
                    msg = input(f"({self.username})--> ")
                except EOFError:
                    break
                if not msg:
                    continue
                if msg == "/shutdown":
                    print(Fore.YELLOW + "[*] Oda kapatılıyor...")
                    self.shutdown()
                    break
                if self._dispatch_command(msg):
                    continue
                self.logger.info(f"{self.username}: {msg}")
                self.broadcast({"type": "chat", "from": self.username, "text": msg})
        except KeyboardInterrupt:
            print(Fore.YELLOW + "\n[*] Bizi tercih ettiğiniz için teşekkürler!")
            self.shutdown()


# ---------------------------------------------------------------------------
# İSTEMCİ
# ---------------------------------------------------------------------------

class ChatClient:
    def __init__(self, server_ip: str, port: int, username: str, password: str | None,
                 connect_timeout: float = 10.0, auto_reconnect: bool = True):
        self.server_ip = server_ip
        self.port = port
        self.username = username
        self.password = password or None
        self.connect_timeout = connect_timeout
        self.auto_reconnect = auto_reconnect

        self.sock: socket.socket | None = None
        self.send_lock = threading.RLock()
        self.state_lock = threading.RLock()
        self.connected = False
        self.running = True
        self.quitting = False

        self.outbound: "queue.Queue[dict]" = queue.Queue()
        self._ping_waiters: dict[float, float] = {}
        self._input_prompt_visible = False
        self.logger = setup_logging("client", "Client_INFO.log")

    # -- yardımcı gösterim ------------------------------------------------
    def _print(self, text: str) -> None:
        # aktif input satırını bozmadan mesaj basar
        print("\r" + " " * 70 + "\r" + text)
        print(f"{self.username}--> ", end="", flush=True)

    def _reprompt(self) -> None:
        print(f"{self.username}--> ", end="", flush=True)

    # -- gönderim -----------------------------------------------------
    def send_or_queue(self, payload: dict, quiet: bool = False) -> None:
        with self.state_lock:
            if self.connected and self.sock:
                try:
                    send_json(self.sock, payload, lock=self.send_lock)
                    return
                except OSError:
                    self.connected = False
            self.outbound.put(payload)
        if not quiet and payload.get("type") in ("chat", "action", "whisper"):
            self._print(Fore.YELLOW + "[*] Bağlantı yok, mesaj kuyruğa alındı; bağlanınca gönderilecek.")

    def _flush_outbound(self) -> None:
        while True:
            try:
                payload = self.outbound.get_nowait()
            except queue.Empty:
                return
            try:
                send_json(self.sock, payload, lock=self.send_lock)
            except OSError:
                self.outbound.put(payload)
                return

    # -- gelen mesajları işleme -----------------------------------------
    def _apply_history(self, history: list[dict]) -> None:
        if not history:
            return
        self._print(Fore.CYAN + "--- kaçırdığınız mesajlar ---")
        for item in history:
            self._render_incoming(item, is_history=True)
        self._print(Fore.CYAN + "--- geçmiş sonu ---")

    def _render_incoming(self, msg: dict, is_history: bool = False) -> None:
        mtype = msg.get("type")
        ts = hhmm(msg.get("ts"))
        marker = "[geçmiş] " if is_history else ""
        if mtype == "chat":
            line = f"{marker}[{ts}] {msg.get('from', '?')}: {msg.get('text', '')}"
            self._print(line)
            self.logger.info(line)
        elif mtype == "action":
            line = f"{marker}[{ts}] * {msg.get('from', '?')} {msg.get('text', '')}"
            self._print(Fore.CYAN + line)
            self.logger.info(line)
        elif mtype == "system":
            line = f"{marker}[{ts}] * {msg.get('text', '')}"
            self._print(Fore.CYAN + line)
            self.logger.info(line)
        elif mtype == "whisper":
            line = f"[{ts}] (fısıltı) {msg.get('from', '?')}: {msg.get('text', '')}"
            self._print(Fore.MAGENTA + line)
            self.logger.info(line)
        elif mtype == "whisper_sent":
            line = f"[{ts}] (fısıltı -> {msg.get('to', '?')}): {msg.get('text', '')}"
            self._print(Fore.MAGENTA + line)

    def _handle_message(self, msg: dict) -> bool:
        """True dönerse bağlantı sonlandırılmalı."""
        mtype = msg.get("type")
        if mtype in ("chat", "action", "system", "whisper", "whisper_sent"):
            self._render_incoming(msg)
        elif mtype == "topic":
            self._print(Fore.CYAN + f"* Oda konusu: {msg.get('text', '')}")
        elif mtype == "userlist":
            self._print(Fore.CYAN + "[*] Odadakiler: " + ", ".join(msg.get("users", [])))
        elif mtype == "nick_ack":
            self.username = msg.get("username", self.username)
            self._print(Fore.GREEN + f"[*] Kullanıcı adınız artık: {self.username}")
        elif mtype == "heartbeat_ack":
            pass
        elif mtype == "pong":
            echo_ts = msg.get("echo_ts")
            if echo_ts is not None:
                rtt_ms = (time.time() - echo_ts) * 1000
                self._print(Fore.CYAN + f"[*] Ping: {rtt_ms:.0f} ms")
        elif mtype == "kick":
            reason = msg.get("reason") or ""
            suffix = f" (sebep: {reason})" if reason else ""
            self._print(Fore.RED + f"[!] Odadan atıldınız{suffix}.")
            self.quitting = True
            return True
        elif mtype == "shutdown":
            self._print(Fore.RED + "[!] Oda sahibi odayı kapattı.")
            self.quitting = True
            return True
        return False

    # -- bağlantı yönetimi (arka plan iş parçacığı) ------------------------
    def _connect_once(self) -> str:
        """'ok' | 'reject' | 'error' döner."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.connect_timeout)
        try:
            sock.connect((self.server_ip, self.port))
        except OSError as e:
            self._print(Fore.RED + f"[!] Bağlanılamadı: {e}")
            try:
                sock.close()
            except OSError:
                pass
            return "error"

        enable_tcp_keepalive(sock)
        send_json(sock, {"type": "hello", "username": self.username, "password": self.password})

        receiver = LineReceiver(sock, timeout=self.connect_timeout)
        first = None
        for msg in receiver.messages():
            if msg.get("type") == "__timeout__":
                self._print(Fore.RED + "[!] Sunucudan yanıt alınamadı (zaman aşımı).")
                sock.close()
                return "error"
            first = msg
            break

        if not first or first.get("type") == "reject":
            reason = (first or {}).get("reason", "bilinmiyor")
            reasons_tr = {
                "invalid_password": "şifre hatalı",
                "invalid_username": "kullanıcı adı geçersiz",
                "room_full": "oda dolu",
            }
            self._print(Fore.RED + f"[!] Bağlantı reddedildi: {reasons_tr.get(reason, reason)}")
            sock.close()
            return "reject"

        if first.get("type") != "welcome":
            sock.close()
            return "error"

        with self.state_lock:
            self.sock = sock
            self.connected = True
        self.logger.info(f"Connected to {self.server_ip}:{self.port} as {self.username}")
        self._print(Fore.GREEN + f"[*] Odaya bağlanıldı! Host: {first.get('username', '?')}")
        topic = first.get("topic")
        if topic:
            self._print(Fore.CYAN + f"* Oda konusu: {topic}")
        self._flush_outbound()
        self._apply_history(first.get("history", []))

        sock.settimeout(SOCKET_POLL_TIMEOUT)
        last_activity = time.time()
        last_heartbeat = 0.0
        for msg in receiver.messages():
            if msg.get("type") == "__timeout__":
                now = time.time()
                if now - last_activity > IDLE_DISCONNECT_AFTER:
                    self._print(Fore.YELLOW + "[!] Sunucudan uzun süredir yanıt yok, bağlantı yeniden kuruluyor...")
                    break
                if now - max(last_heartbeat, last_activity) > HEARTBEAT_INTERVAL:
                    try:
                        send_json(sock, {"type": "heartbeat"}, lock=self.send_lock)
                        last_heartbeat = now
                    except OSError:
                        break
                continue
            last_activity = time.time()
            if self._handle_message(msg):
                with self.state_lock:
                    self.connected = False
                try:
                    sock.close()
                except OSError:
                    pass
                return "closed"

        with self.state_lock:
            self.connected = False
        try:
            sock.close()
        except OSError:
            pass
        return "dropped"

    def _connection_manager(self) -> None:
        attempt = 0
        while self.running and not self.quitting:
            result = self._connect_once()
            if result in ("closed", "reject"):
                self.running = False
                break
            if not self.auto_reconnect:
                self.running = False
                break
            if not self.running or self.quitting:
                break
            delay = RECONNECT_DELAYS[min(attempt, len(RECONNECT_DELAYS) - 1)]
            attempt += 1
            self._print(Fore.YELLOW + f"[*] {delay} saniye sonra yeniden bağlanılacak (deneme {attempt})...")
            for _ in range(int(delay * 10)):
                if not self.running or self.quitting:
                    break
                time.sleep(0.1)
            if result == "ok":
                attempt = 0
        os._exit(0) if self.quitting and result in ("closed",) else None

    def _dispatch_command(self, msg: str) -> bool:
        if msg == "/help":
            print(HELP_COMMON)
            print(HELP_CLIENT_EXTRA)
        elif msg in ("/users", "/list"):
            self.send_or_queue({"type": "list_request"}, quiet=True)
        elif msg.startswith("/nick "):
            new_name = msg.split(" ", 1)[1].strip()[:32]
            self.send_or_queue({"type": "nick", "new": new_name})
        elif msg.startswith("/msg ") or msg.startswith("/w "):
            _, rest = msg.split(" ", 1)
            if " " not in rest:
                print(Fore.RED + "[!] Kullanım: /msg <kullanici> <mesaj>")
            else:
                target, text = rest.split(" ", 1)
                self.send_or_queue({"type": "whisper", "to": target, "text": text})
        elif msg.startswith("/me "):
            action = msg.split(" ", 1)[1]
            self.send_or_queue({"type": "action", "text": action})
            self.logger.info(f"* {self.username} {action}")
        elif msg == "/ping":
            self.send_or_queue({"type": "ping", "ts": time.time()}, quiet=True)
        elif msg == "/clear":
            clear_screen()
        elif msg in ("/quit", "/exit"):
            self.quitting = True
            self.running = False
            self.send_or_queue({"type": "bye"}, quiet=True)
        else:
            return False
        return True

    def run(self) -> None:
        print(f"[*] {self.server_ip}:{self.port} adresine bağlanılıyor...")
        mgr_thread = threading.Thread(target=self._connection_manager, daemon=True)
        mgr_thread.start()

        try:
            while self.running:
                try:
                    msg = input(f"{self.username}--> ")
                except EOFError:
                    break
                if not msg:
                    continue
                if self._dispatch_command(msg):
                    if msg in ("/quit", "/exit"):
                        break
                    continue
                if len(msg) > MAX_MESSAGE_LEN:
                    print(Fore.RED + f"[!] Mesaj çok uzun (azami {MAX_MESSAGE_LEN} karakter).")
                    continue
                self.logger.info(f"{self.username}: {msg}")
                self.send_or_queue({"type": "chat", "text": msg})
        except KeyboardInterrupt:
            print(Fore.YELLOW + "\n[*] Bizi tercih ettiğiniz için teşekkürler!")
        finally:
            self.quitting = True
            self.running = False
            with self.state_lock:
                if self.sock:
                    try:
                        self.sock.close()
                    except OSError:
                        pass


# ---------------------------------------------------------------------------
# GİRİŞ NOKTASI
# ---------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(description="Chatroom - kısıtlı internete dayanıklı terminal sohbeti")
    parser.add_argument("--no-color", action="store_true", help="Renkli çıktıyı kapat")
    sub = parser.add_subparsers(dest="mode")

    p_host = sub.add_parser("host", help="Yeni bir sohbet odası aç")
    p_host.add_argument("--bind", default=None, help="Bağlanılacak IP (varsayılan: 0.0.0.0)")
    p_host.add_argument("--port", type=int, default=None)
    p_host.add_argument("--username", default=None)
    p_host.add_argument("--password", default=None, help="Oda şifresi (opsiyonel)")
    p_host.add_argument("--max-clients", type=int, default=DEFAULT_MAX_CLIENTS)
    p_host.add_argument("--history", type=int, default=DEFAULT_HISTORY_SIZE)

    p_join = sub.add_parser("join", help="Var olan bir odaya katıl")
    p_join.add_argument("--ip", default=None, help="Sunucu IP adresi")
    p_join.add_argument("--port", type=int, default=None)
    p_join.add_argument("--username", default=None)
    p_join.add_argument("--password", default=None, help="Oda şifresi (varsa)")
    p_join.add_argument("--timeout", type=float, default=10.0, help="Bağlantı zaman aşımı (sn)")
    p_join.add_argument("--no-reconnect", action="store_true", help="Otomatik yeniden bağlanmayı kapat")

    return parser.parse_args()


def interactive_fill(mode: str, args, ask_password: bool = False) -> None:
    """Eksik ZORUNLU alanları interaktif olarak sorar. --password bilerek
    hariç tutulur: komut satırından mod verildiyse (host/join alt komutu
    kullanıldıysa) verilmeyen --password sessizce "şifre yok" anlamına
    gelir, kullanıcı beklenmedik bir soruyla karşılaşmaz. Şifre yalnızca
    hiç alt komut verilmeyip tam interaktif akışa girildiğinde (ask_password
    ile) sorulur."""
    if mode == "host":
        if not args.bind:
            args.bind = input("Bind IP (boş bırakırsanız 0.0.0.0): ") or "0.0.0.0"
        if not args.port:
            args.port = int(input("Bind Port (5000+ önerilir): "))
        if not args.username:
            args.username = input("Kullanıcı adınız: ")
        if ask_password and args.password is None:
            args.password = input("Oda şifresi (opsiyonel, boş geçebilirsiniz): ") or None
    else:
        if not args.ip:
            args.ip = input("Sunucu IP: ")
        if not args.port:
            args.port = int(input("Sunucu Port: "))
        if not args.username:
            args.username = input("Kullanıcı adınız: ")
        if ask_password and args.password is None:
            args.password = input("Oda şifresi (varsa girin, yoksa boş geçin): ") or None


def main() -> None:
    args = parse_args()
    if args.no_color:
        global Fore, Style
        class _NoColor:
            def __getattr__(self, _name):
                return ""
        Fore = _NoColor()
        Style = _NoColor()

    print(Fore.RED + "Bu uygulama loglama sistemine sahiptir, lütfen saygı çerçevesinde konuşun.")
    print(BANNER)

    mode = args.mode
    fully_interactive = mode not in ("host", "join")
    if fully_interactive:
        choice = input("Oda mı açacaksınız yoksa bir odaya mı katılacaksınız? [H]ost / [J]oin: ").strip().lower()
        mode = "host" if choice.startswith("h") else "join"

        class _Ns:
            pass

        new_args = _Ns()
        new_args.bind = new_args.ip = new_args.port = new_args.username = None
        new_args.password = None
        new_args.max_clients = DEFAULT_MAX_CLIENTS
        new_args.history = DEFAULT_HISTORY_SIZE
        new_args.timeout = 10.0
        new_args.no_reconnect = False
        args = new_args

    interactive_fill(mode, args, ask_password=fully_interactive)

    try:
        my_ip = socket.gethostbyname(socket.gethostname())
        print(f"[*] Bu makinenin yerel IP adresi: {my_ip}")
    except OSError:
        pass

    if mode == "host":
        server = ChatServer(args.bind or "0.0.0.0", args.port, args.username, args.password,
                             max_clients=args.max_clients, history_size=args.history)
        server.run()
    else:
        client = ChatClient(args.ip, args.port, args.username, args.password,
                             connect_timeout=args.timeout, auto_reconnect=not args.no_reconnect)
        client.run()


if __name__ == "__main__":
    main()
