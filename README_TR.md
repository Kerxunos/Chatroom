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

> **Python socket'leri ile geliştirilmiş, güvenilir ve terminal tabanlı çok istemcili sohbet uygulaması.**

Chatroom, **kararsız veya kısıtlı internet bağlantılarında bile kullanılabilirliğini korumak** amacıyla geliştirilmiş, hafif ve terminal tabanlı bir **istemci-sunucu (client-server) sohbet uygulamasıdır**.

Basit bir socket sohbet uygulamasından farklı olarak Chatroom; otomatik yeniden bağlanma, uygulama seviyesinde heartbeat, mesaj kuyruğu, mesaj geçmişi kurtarma, hız sınırlaması, özel mesajlaşma, oda moderasyonu ve isteğe bağlı şifre koruması gibi özellikler içerir.

**Sürüm:** `4.0`
**Dil:** Python 3
**Lisans:** GPL-3.0

---

## ✨ Özellikler

### 💬 Gerçek Zamanlı Mesajlaşma

* Çok istemcili TCP iletişimi
* Gerçek zamanlı mesaj yayınlama
* Özel mesajlaşma
* Aksiyon mesajları
* Kullanıcı adı değiştirme
* Çevrimiçi kullanıcı listesini görüntüleme
* Oda konusu belirleme

### 🌐 Bağlantı Güvenilirliği

Chatroom, **güvenilir olmayan veya sık sık kopan bağlantılar** göz önünde bulundurularak tasarlanmıştır.

* 🔄 Otomatik yeniden bağlanma
* ❤️ Uygulama seviyesinde heartbeat
* 🔌 TCP keepalive
* 📦 Giden mesaj kuyruğu
* 🕐 Bağlantı zaman aşımı tespiti
* 📜 Yeniden bağlanma sonrası mesaj geçmişi kurtarma
* ⏳ Kademeli yeniden bağlanma süreleri

Bağlantı geçici olarak kesildiğinde kullanıcı tarafından yazılan mesajlar **doğrudan kaybolmak yerine kuyruğa alınır**.

Bağlantı yeniden kurulduğunda bekleyen mesajlar otomatik olarak gönderilir.

### 🛡️ Spam Koruması

Sunucu, istemcilerin ne kadar hızlı mesaj gönderebileceğini sınırlar.

Mevcut limitler:

```text
Maksimum mesaj uzunluğu: 1000 karakter
Hız limiti:              4 saniyede 6 mesaj
```

Bu sistem, tek bir istemcinin aşırı miktarda trafik oluşturmasını veya sohbet odasını spam ile doldurmasını önlemeye yardımcı olur.

### 🔐 Şifre Korumalı Odalar

Host, oluşturduğu odayı isteğe bağlı olarak şifre ile koruyabilir.

```bash
python chatroom.py host --port 5000 --username Kerxunos --password 1234
```

İstemciler daha sonra şifreyi kullanarak odaya katılabilir:

```bash
python chatroom.py join --ip 127.0.0.1 --port 5000 --username Ayse --password 1234
```

### 👑 Host Moderasyonu

Oda sahibi aşağıdaki yönetim komutlarına sahiptir:

* `/mute`
* `/unmute`
* `/kick`
* `/topic`
* `/shutdown`

Bu sayede oda sahibi ayrı bir yönetim arayüzüne ihtiyaç duymadan sohbeti yönetebilir.

### 📝 Loglama

Sunucu ve istemci aktiviteleri otomatik olarak loglanabilir.

```text
Server_INFO.log
Client_INFO.log
```

Log dosyaları `append` modunda tutulur; önceki oturumların logları otomatik olarak silinmez.

---

# 🏗️ Mimari

Chatroom, klasik bir **TCP istemci-sunucu mimarisi** kullanır.

```text
                         ┌─────────────────────┐
                         │       HOST          │
                         │                     │
                         │   ChatServer        │
                         │   TCP Socket        │
                         │   Oda Yönetimi      │
                         │   Moderasyon        │
                         │   Mesaj Geçmişi     │
                         └──────────┬──────────┘
                                    │
                         TCP / JSON │
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
              ▼                     ▼                     ▼
       ┌─────────────┐       ┌─────────────┐       ┌─────────────┐
       │   İSTEMCİ   │       │   İSTEMCİ   │       │   İSTEMCİ   │
       │             │       │             │       │             │
       │ ChatClient  │       │ Mesaj Kuyruğu│      │ Heartbeat   │
       │ Auto-Reconn │       │             │       │             │
       └─────────────┘       └─────────────┘       └─────────────┘
```

Sunucu, bağlı istemcileri yönetir ve mesajları yayınlar.

İstemciler ise sunucuyla **JSON-over-TCP** tabanlı hafif bir iletişim protokolü üzerinden haberleşir.

---

# 🔌 İletişim Protokolü

Chatroom basit ve satır tabanlı bir iletişim protokolü kullanır.

Her mesaj:

```text
JSON + newline
```

formatında gönderilir.

Örneğin:

```json
{
  "type": "chat",
  "text": "Herkese merhaba!"
}
```

TCP akış tabanlı olduğu için tek bir `recv()` çağrısında bir mesajın tamamı veya birden fazla mesaj gelebilir.

Bu problem, uygulama içerisindeki `LineReceiver` sınıfı tarafından çözülür.

### Desteklenen mesaj tiplerinden bazıları

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

# 🔄 Bağlantı Kurtarma

Chatroom'un temel amaçlarından biri, geçici ağ problemlerinden sonra bağlantıyı mümkün olduğunca otomatik şekilde toparlamaktır.

## Otomatik Yeniden Bağlanma

İstemcinin bağlantısı kesildiğinde uygulama otomatik olarak yeniden bağlanmayı dener.

Bekleme süreleri:

```text
1 saniye
2 saniye
5 saniye
10 saniye
15 saniye
30 saniye
...
```

Başarılı bir bağlantı kurulduğunda yeniden deneme sayacı sıfırlanır.

---

## 📦 Mesaj Kuyruğu

Bağlantı kesildiği sırada yazılan mesajlar bir **outbound queue** içerisine alınır.

```text
Kullanıcı mesaj yazar
        │
        ▼
Bağlantı var mı?
   ┌────┴────┐
  EVET      HAYIR
   │          │
   ▼          ▼
 Gönder      Kuyruğa al
               │
               ▼
        Bağlantı yeniden kurulur
               │
               ▼
        Kuyruktaki mesajları
             gönder
```

Bu sayede ağ bağlantısı geçici olarak kesildiğinde mesajlar doğrudan kaybolmaz.

---

# ❤️ Heartbeat Sistemi

Chatroom bağlantı kontrolü için iki farklı mekanizma kullanır.

### TCP Keepalive

Destekleyen işletim sistemlerinde socket'ler TCP keepalive özelliği ile yapılandırılır.

### Uygulama Seviyesinde Heartbeat

İstemci belirli aralıklarla:

```json
{
  "type": "heartbeat"
}
```

mesajını gönderir.

Sunucu ise:

```json
{
  "type": "heartbeat_ack"
}
```

cevabını gönderir.

Bu sistem, TCP seviyesinde hâlâ açık gibi görünen fakat gerçekte kullanılamayan bağlantıların daha hızlı tespit edilmesini sağlar.

---

# 📜 Mesaj Geçmişi

Sunucu, son mesajların sınırlı bir bölümünü hafızada tutar.

Varsayılan:

```text
30 mesaj
```

Bir istemci yeniden bağlandığında sunucu, hoş geldin mesajı ile birlikte mevcut kısa mesaj geçmişini de gönderir.

İstemci bunu şu şekilde gösterir:

```text
--- kaçırdığınız mesajlar ---
[geçmiş] [14:21] Kerem: Merhaba
[geçmiş] [14:21] Ayşe: Selam!
[geçmiş] [14:22] Kerem: Nasılsınız?
--- geçmiş sonu ---
```

Mesaj geçmişi kalıcı bir veritabanı değildir ve bellekte sınırlı bir pencere olarak tutulur.

---

# 👥 Çoklu İstemci Desteği

Sunucu aynı anda birden fazla istemciyi destekler.

Varsayılan maksimum istemci sayısı:

```text
25 istemci
```

Bu değer sunucu başlatılırken değiştirilebilir:

```bash
python chatroom.py host \
    --port 5000 \
    --username Kerxunos \
    --max-clients 50
```

---

# 💻 Kurulum

## Gereksinimler

* Python **3.10+**
* TCP/IP ağ bağlantısı
* `colorama`

Diğer işlevlerin büyük bölümü Python'un standart kütüphanesi kullanılarak gerçekleştirilir.

### Bağımlılığı yükleme

```bash
pip install colorama
```

veya:

```bash
python -m pip install colorama
```

---

# 🚀 Hızlı Başlangıç

## 1. Repository'yi klonla

```bash
git clone https://github.com/Kerxunos/Chatroom.git
cd Chatroom
```

## 2. Sunucuyu başlat

```bash
python chatroom.py host --port 5000 --username Kerxunos
```

Şuna benzer bir çıktı göreceksin:

```text
[*] Oda açıldı -> 0.0.0.0:5000
```

## 3. İstemci ile bağlan

Başka bir terminalde veya başka bir bilgisayarda:

```bash
python chatroom.py join \
    --ip 127.0.0.1 \
    --port 5000 \
    --username Ayse
```

Artık sohbet etmeye başlayabilirsiniz.

---

# 🔐 Şifre Korumalı Oda

### Host

```bash
python chatroom.py host \
    --port 5000 \
    --username Kerxunos \
    --password 1234
```

### İstemci

```bash
python chatroom.py join \
    --ip 127.0.0.1 \
    --port 5000 \
    --username Ayse \
    --password 1234
```

Şifre yanlışsa sunucu bağlantıyı reddeder.

---

# 🖥️ İnteraktif Mod

Tüm parametreleri manuel olarak girmek zorunda değilsiniz.

Sadece:

```bash
python chatroom.py
```

çalıştırarak interaktif kurulum ekranını açabilirsiniz.

Uygulama size:

```text
Oda mı açacaksınız yoksa bir odaya mı katılacaksınız?
[H]ost / [J]oin:
```

şeklinde seçim yaptırır ve gerekli bilgileri adım adım ister.

---

# ⌨️ Komutlar

## 👤 Genel Komutlar

Herkes tarafından kullanılabilir:

| Komut                      | Açıklama                          |
| -------------------------- | --------------------------------- |
| `/help`                    | Kullanılabilir komutları gösterir |
| `/users`                   | Odadaki kullanıcıları listeler    |
| `/list`                    | `/users` ile aynı işlev           |
| `/nick <isim>`             | Kullanıcı adını değiştirir        |
| `/msg <kullanıcı> <mesaj>` | Özel mesaj gönderir               |
| `/w <kullanıcı> <mesaj>`   | `/msg` kısayolu                   |
| `/me <eylem>`              | Aksiyon mesajı gönderir           |
| `/clear`                   | Kendi terminalini temizler        |

### Örnek

```text
/msg Ayse Özelden konuşalım.
```

Çıktı:

```text
(fısıltı -> Ayse): Özelden konuşalım.
```

---

# 👤 İstemci Komutları

| Komut   | Açıklama                      |
| ------- | ----------------------------- |
| `/ping` | Sunucuya olan gecikmeyi ölçer |
| `/quit` | Sohbetten ayrılır             |
| `/exit` | `/quit` ile aynı işlev        |

Örnek:

```text
/ping
```

Çıktı:

```text
[*] Ping: 24 ms
```

---

# 👑 Host Komutları

Oda sahibi ek yönetim komutlarına sahiptir.

| Komut                       | Açıklama                                 |
| --------------------------- | ---------------------------------------- |
| `/mute <kullanıcı>`         | Kullanıcının mesaj göndermesini engeller |
| `/unmute <kullanıcı>`       | Susturmayı kaldırır                      |
| `/topic`                    | Mevcut oda konusunu gösterir             |
| `/topic <metin>`            | Oda konusunu değiştirir                  |
| `/kick <kullanıcı>`         | Kullanıcıyı odadan atar                  |
| `/kick <kullanıcı> <sebep>` | Kullanıcıyı belirtilen sebeple atar      |
| `/shutdown`                 | Odayı kapatır                            |

### Örnek

```text
/topic Computer Engineering Room
```

veya:

```text
/kick Ayse Spam yapıldığı için
```

---

# ⚙️ Yapılandırma

Bazı önemli limitler doğrudan kaynak kod içerisinden değiştirilebilir.

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

### Varsayılan değerler

| Ayar                      |                 Varsayılan |
| ------------------------- | -------------------------: |
| Maksimum mesaj uzunluğu   |              1000 karakter |
| Rate limit                |         4 saniyede 6 mesaj |
| Mesaj geçmişi             |                   30 mesaj |
| Maksimum istemci          |                         25 |
| Socket timeout            |                  15 saniye |
| Heartbeat aralığı         |                  20 saniye |
| Idle disconnect           |                  55 saniye |
| Yeniden bağlanma süreleri | 1, 2, 5, 10, 15, 30 saniye |

---

# 🗂️ Loglama

Uygulama sunucu ve istemci aktiviteleri için ayrı log dosyaları oluşturur.

```text
Server_INFO.log
Client_INFO.log
```

Örnek kayıtlar:

```text
2026-09-27 14:20:12 - Server started on 0.0.0.0:5000 as Kerxunos
2026-09-27 14:21:04 - Ayse connected from 192.168.1.25:53142
2026-09-27 14:21:18 - Ayse: Hello everyone!
```

Loglama işlemi Python'un yerleşik `logging` modülü kullanılarak gerçekleştirilir.

---

# 🛡️ Güvenlik

Chatroom bazı temel güvenlik ve kötüye kullanım önleme mekanizmalarına sahiptir:

* Maksimum mesaj uzunluğu
* Rate limiting
* İsteğe bağlı oda şifresi
* Bağlantı zaman aşımı kontrolü
* Maksimum istemci sınırı
* Host moderasyonu
* TCP keepalive
* Kullanıcı adı doğrulaması
* Sınırlı mesaj geçmişi

Ancak **Chatroom şu anda production seviyesinde güvenli bir mesajlaşma sistemi olarak tasarlanmamıştır.**

## Mevcut sınırlamalar

Mevcut iletişim protokolünde JSON mesajları **şifrelenmemiş TCP bağlantısı** üzerinden gönderilir.

Şu anda aşağıdaki özellikler bulunmamaktadır:

* TLS şifreleme
* Uçtan uca şifreleme (E2EE)
* Kullanıcı hesap sistemi
* Kalıcı kimlik doğrulama
* Şifre hashleme
* Veritabanı tabanlı kullanıcı yönetimi

Bu nedenle mevcut haliyle uygulama üzerinden hassas veya gizli bilgilerin gönderilmesi önerilmez.

Uygulama güvenilmeyen veya halka açık ağlarda kullanılacaksa ek güvenlik mekanizmaları uygulanmalıdır.

---

# 🧠 Teknik Özellikler

Bu proje yalnızca basit bir socket sohbet uygulaması oluşturmak amacıyla değil, **gerçek ağ programlama problemlerini deneyimlemek** amacıyla geliştirilmiştir.

### Python Networking

```python
socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)
```

Uygulama güvenilir veri aktarımı için TCP socket'lerini kullanır.

### Çoklu İş Parçacığı

Sunucu her istemci bağlantısı için ayrı bir daemon thread oluşturur:

```python
threading.Thread(
    target=self._handle_client,
    args=(conn, addr),
    daemon=True
)
```

Bu sayede birden fazla istemci aynı anda iletişim kurabilir.

### Thread Safety

Paylaşılan sunucu verileri:

```python
threading.RLock()
```

ile korunur.

Bu özellikle:

* İstemci listesi
* Mesaj yayınlama
* Kullanıcı adı yönetimi
* Bağlantı işlemleri

için önemlidir.

### Queue Tabanlı Mesaj Gönderimi

İstemci:

```python
queue.Queue()
```

kullanarak bağlantı kesildiğinde gönderilecek mesajları geçici olarak saklar.

### Verimli Mesaj Geçmişi

Son mesajlar:

```python
collections.deque
```

kullanılarak maksimum boyutu sınırlandırılmış şekilde tutulur.

Bu sayede mesaj geçmişinin bellekte sınırsız şekilde büyümesi engellenir.

---

# 📁 Proje Yapısı

Uygulama şu anda hafif ve tek dosyalı bir mimari üzerine kuruludur:

```text
Chatroom/
│
├── chatroom.py
├── LICENSE
├── README.md
│
├── Server_INFO.log      # çalışma sırasında oluşturulur
└── Client_INFO.log      # çalışma sırasında oluşturulur
```

Log dosyaları çalışma sırasında otomatik olarak oluşturulur ve projenin temel kaynak kodunun bir parçası değildir.

---

# 🧪 Örnek Oturum

### Host

```text
$ python chatroom.py host --port 5000 --username Kerxunos

[*] Oda açıldı -> 0.0.0.0:5000
Komutlar için /help yazın.
```

### İstemci

```text
$ python chatroom.py join \
    --ip 192.168.1.10 \
    --port 5000 \
    --username Ayse

[*] 192.168.1.10:5000 adresine bağlanılıyor...
[*] Odaya bağlanıldı! Host: Kerxunos
```

### Sohbet

```text
Ayse--> Merhaba!

[14:32] Ayse: Merhaba!
[14:32] Kerxunos: Hoş geldin!
```

### Geçici bağlantı kaybı

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

# 🗺️ Yol Haritası

Gelecekte eklenmesi planlanan veya geliştirilebilecek özellikler:

* [ ] 🔐 TLS şifreleme
* [ ] 🔑 Güvenli kimlik doğrulama
* [ ] 🗄️ Kalıcı mesaj depolama
* [ ] 🧪 Otomatik unit ve integration testleri
* [ ] 📊 Gelişmiş bağlantı istatistikleri
* [ ] 🖥️ Geliştirilmiş terminal arayüzü
* [ ] 🌍 İngilizce dil desteği
* [ ] 🔒 Şifre hashleme
* [ ] 🛡️ Daha güçlü input validation
* [ ] 📦 `requirements.txt` ile bağımlılık yönetimi
* [ ] 🐳 Docker desteği
* [ ] ⚡ Performans iyileştirmeleri
* [ ] 📚 Ayrıntılı protokol dokümantasyonu
* [ ] 🔄 Daha gelişmiş reconnect/session yönetimi

---

# 🤝 Katkıda Bulunma

Projeye katkıda bulunmak, hata bildirmek veya yeni özellik önermek isterseniz:

### 1. Repository'yi fork edin.

### 2. Yeni bir branch oluşturun.

```bash
git checkout -b feature/my-feature
```

### 3. Değişikliklerinizi commit edin.

```bash
git commit -m "Add my feature"
```

### 4. Branch'i GitHub'a gönderin.

```bash
git push origin feature/my-feature
```

### 5. Pull Request oluşturun.

---

# ⚠️ Yasal Uyarı

Chatroom temel olarak **eğitim ve deneysel ağ programlama projesi** olarak geliştirilmiştir.

Uygulamayı başkalarının ağ trafiğini izlemek, kişisel bilgilerini toplamak veya yetkisiz erişim sağlamak amacıyla kullanmayın.

Yazılımın yanlış veya yetkisiz kullanımından doğabilecek zararlardan geliştirici sorumlu değildir.

---

# 📜 Lisans

Bu proje **GNU General Public License v3.0 (GPL-3.0)** altında lisanslanmıştır.

Lisansın tamamı için [`LICENSE`](LICENSE) dosyasına bakabilirsiniz.

---

# 👨‍💻 Geliştirici

## Kerxunos

İlgilendiği alanlar:

* 🐍 Python
* 🌐 Network Programming
* 🔐 Cybersecurity
* 🖥️ Software Development
* ☁️ Cloud Technologies

GitHub: **[github.com/Kerxunos](https://github.com/Kerxunos)**

---

<p align="center">

### 💬 Chatroom

**Basit arayüz. Güvenilir iletişim. Python ile geliştirildi.**

Made with 🐍 and ☕ by **Kerxunos**

</p>
