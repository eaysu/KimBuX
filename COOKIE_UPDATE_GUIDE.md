# Cookie Güncelleme Rehberi

Twikit çalışması için **güncel** cookie'ler gerekiyor. Cookie'ler genellikle birkaç saat/gün içinde expire oluyor.

## Adımlar

### 1. Chrome'da Twitter'a Login Ol
- https://x.com adresine git
- Hesabına giriş yap
- Ana sayfada olduğundan emin ol

### 2. Cookie Extension Yükle
- **EditThisCookie** extension'ını yükle:
  https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg

### 3. Cookie'leri Export Et
1. x.com'dayken extension ikonuna tıkla
2. Sağ altta **"Export"** butonuna tıkla
3. **"JSON"** formatını seç (varsayılan)
4. Kopyala

### 4. cookies.txt Dosyasını Güncelle
1. Proje dizininde `cookies.txt` dosyasını aç
2. Tüm içeriği sil
3. Kopyaladığın JSON'u yapıştır
4. Kaydet

### 5. JSON'u Twikit Formatına Çevir
```bash
conda activate tw_env
python convert_chrome_cookies.py
```

### 6. Test Et
```bash
python main.py elonmusk 100
```

## Sorun Giderme

### "Couldn't get KEY_BYTE indices" Hatası
- Cookie'ler expire olmuş olabilir → Adım 1'den tekrar başla
- Twitter hesabın kilitli olabilir → x.com'da kontrol et

### "403 Forbidden" Hatası
- Cookie'ler yok veya geçersiz → Yeni cookie export et
- IP engellenmiş olabilir → VPN dene

### "Rate Limit" Hatası
- Çok fazla istek yapılmış → 15 dakika bekle
- Farklı hesap dene

## Önemli Notlar

- Cookie'ler **kişisel** ve **gizli** bilgilerdir
- `.gitignore` dosyasında `cookies.txt` ve `cookies.json` var
- Cookie'leri kimseyle paylaşma
- Her 24 saatte bir yeni cookie export etmen gerekebilir
