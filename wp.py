from pyrogram import Client, filters
import sqlite3
import pywhatkit as kit
import datetime
import re
import asyncio

# Selenium ayarları (EKLENDİ)
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import os

# Telegram API bilgileri
API_ID = 21975331
API_HASH = "b093d17566449ed473cbdbe6ef7391ea"
PHONE_NUMBER = "+50379657082"
OWNER_ID = 1331544490

# Takip edilecek Telegram kanal ve grupları
BONUSSOFT_CHANNELS = [
    -1001513128130, -1001429032175, -1001361953435, -1002205804507,
    -1001895945898, -1001595792569, -1001904588149, -1001925728559,
    -1001585898045, -1002254425065, -1002696377133, -1001721415718,
    -1001961458338, -1002321250370, -1001969781945, -1002162241096,
    -1001612421368, -1001528160850, -1002291105468, -1002402728990,
    -1002621151191
]

# Selenium ile WhatsApp Web'e giriş (EKLENDİ)
def selenium_ayar():
    chrome_options = Options()
    chrome_options.add_argument('--user-data-dir=C:\\ChromeProfile')  # Profil kaydı için
    chrome_options.add_argument('--profile-directory=Default')
    chrome_options.add_argument('--disable-infobars')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    driver_path = os.path.join(os.getcwd(), "chromedriver.exe")  # Aynı klasörde olmalı
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get("https://web.whatsapp.com")

    print("QR kodu okutup giriş yapman için 60 saniye bekleniyor...")
    time.sleep(60)  # QR okutma süresi
    driver.quit()

# Veritabanı bağlantısı
conn = sqlite3.connect("promosyonlar.db")
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS promosyonlar
             (kod TEXT, link TEXT, kanal_id INTEGER)''')
conn.commit()

# WhatsApp'a mesaj gönderen fonksiyon
def whatsapp_mesaj_gonder(grup_adi, mesaj):
    try:
        now = datetime.datetime.now()
        saat = now.hour
        dakika = now.minute + 1  # Mesajı 1 dakika sonrasına ayarlıyoruz
        kit.sendwhatmsg_to_group(grup_adi, mesaj, saat, dakika)
        print(f"✅ WhatsApp grubuna mesaj gönderildi: {mesaj}")
    except Exception as e:
        print(f"❌ WhatsApp mesaj gönderme hatası: {e}")

# Telegram client başlatılıyor
app = Client("bonussoft_session", api_id=API_ID, api_hash=API_HASH, phone_number=PHONE_NUMBER)

# Promosyon kodu ve link ayıklama fonksiyonu
def promosyon_ayikla(metin):
    kod = None
    link = None

    kodlar = re.findall(r'\b[A-Z0-9]{6,20}\b', metin)
    linkler = re.findall(r'https?://\S+', metin)

    if kodlar and linkler:
        kod = kodlar[0]
        link = linkler[0]
    return kod, link

# Mesaj geldiğinde tetiklenen event
@app.on_message(filters.chat(BONUSSOFT_CHANNELS))
async def mesaj_kontrol(client, message):
    try:
        if message.text:
            code, link = promosyon_ayikla(message.text)

            if code and link:
                # Veritabanında var mı kontrol et
                c.execute("SELECT * FROM promosyonlar WHERE kod=? AND link=?", (code, link))
                data = c.fetchone()

                if not data:
                    # Yeni promosyon kaydet
                    c.execute("INSERT INTO promosyonlar (kod, link, kanal_id) VALUES (?, ?, ?)", (code, link, message.chat.id))
                    conn.commit()
                    print(f"✅ Yeni promosyon bulundu: {code} - {link}")

                    # WhatsApp YÖNETİM grubuna gönder
                    whatsapp_mesaj_gonder("YÖNETİM", f"{code} - {link}")
                else:
                    print("⚠️ Bu promosyon zaten kayıtlı.")
    except Exception as e:
        print(f"❌ Mesaj işleme hatası: {e}")

# QR kod okutulacak (SADECE ilk çalıştırmada gerek)
selenium_ayar()

# Botu başlat
print("Bot başlatılıyor...")
app.run()
