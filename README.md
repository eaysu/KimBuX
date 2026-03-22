# KimBuX - Twitter/X Account Analyzer

Twitter/X hesaplarını analiz eden CLI aracı. GPT destekli profil analizi, kelime frekansları, n-gram'lar ve daha fazlası.

## Kurulum

```bash
pip install -r requirements.txt
```

## Konfigürasyon

1. `.env.example` dosyasını `.env` olarak kopyalayın
2. Gerekli bilgileri doldurun:

```bash
# Twitter Credentials (not used - cookie-based auth)
TWITTER_USERNAME="your_username"
TWITTER_EMAIL="your_email@example.com"
TWITTER_PASSWORD="your_password"

# OpenAI
OPENAI_API_KEY=sk-your-key

# Neon PostgreSQL
DATABASE_URL=postgresql://...
```

## Twitter Authentication (Cookie-Based)

Twikit cookie-based authentication kullanıyor. Cookie'leri Chrome'dan export etmen gerekiyor.

### Cookie Export Adımları

1. **Chrome'da x.com'a login ol**
2. **EditThisCookie extension'ını yükle:**
   - https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg

3. **x.com'dayken:**
   - Extension ikonuna tıkla
   - "Export" → "JSON" formatını seç
   - Kopyala

4. **Proje dizininde `cookies.txt` oluştur** ve JSON'u yapıştır

5. **Converter'ı çalıştır:**
   ```bash
   python convert_chrome_cookies.py
   ```

6. **Test et:**
   ```bash
   python main.py elonmusk 100
   ```

**Not:** Cookie'ler genellikle birkaç saat/gün içinde expire oluyor. Hata alırsan adımları tekrarla.

Detaylı rehber: `COOKIE_UPDATE_GUIDE.md`

## Kullanım

```bash
# Direkt kullanım
python main.py elonmusk 100

# İnteraktif mod
python main.py
```

## Özellikler

- ✅ Son 100/250/500 tweet analizi (original + quote tweets)
- ✅ GPT-4o-mini ile profil analizi
- ✅ Top liked tweets (all-time + recent 30 days)
- ✅ Kelime frekansları ve bigram/trigram analizi
- ✅ MBTI tahmini (eğlence amaçlı)
- ✅ Ton, hedef kitle ve konu analizi
- ✅ PostgreSQL cache (TTL: aktif hesaplar 15 gün, diğerleri 30 gün)
- ✅ Negatif cache (user not found, rate limit, vb.)
- ✅ Rich terminal output

## Veritabanı

Neon PostgreSQL kullanılıyor. Tablolar otomatik oluşturulur.

## Sorun Giderme

### "Couldn't get KEY_BYTE indices"
- Cookie'ler expire olmuş → Yeni cookie export et

### "403 Forbidden"
- Cookie'ler geçersiz → Cookie export adımlarını tekrarla

### "Rate Limit"
- Çok fazla istek → 15 dakika bekle

## Proje Yapısı

```
KimBuX/
├── main.py                      # CLI entry point
├── src/
│   ├── config.py               # Configuration
│   ├── twitter_client.py       # Twikit wrapper
│   ├── text_processor.py       # Text cleaning & n-grams
│   ├── analyzer.py             # Statistics computation
│   ├── gpt_analyzer.py         # GPT analysis
│   ├── database.py             # PostgreSQL cache
│   └── display.py              # Rich terminal output
├── convert_chrome_cookies.py   # Cookie converter
├── cookies.json                # Twikit cookies (auto-generated)
└── COOKIE_UPDATE_GUIDE.md      # Detailed cookie guide
```
