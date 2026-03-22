# KimBuX Deploy Rehberi

## Mimari

KimBuX iki parçadan oluşur:

| Parça | Teknoloji | Deploy |
|-------|-----------|--------|
| **Frontend** | Next.js | Netlify |
| **Backend** | FastAPI (Python) | Render / Railway |

> ⚠️ Netlify yalnızca frontend (static/SSR) için uygundur. Python backend **Netlify'a deploy edilemez** — ayrı bir sunucuya ihtiyaç duyar.

---

## 1. Frontend — Netlify'a Deploy

### Ön Hazırlık

```bash
cd web
npm run build   # hata olmadığından emin ol
```

### Ortam Değişkenleri (Netlify Dashboard → Site Settings → Environment Variables)

```
NEXT_PUBLIC_API_URL=https://your-backend-url.onrender.com
```

### Netlify Ayarları

| Ayar | Değer |
|------|-------|
| Base directory | `web` |
| Build command | `npm run build` |
| Publish directory | `web/.next` |
| Node version | `18` veya `20` |

### Deploy Yöntemleri

**A) Git ile (önerilen):**
1. GitHub repo'yu Netlify'a bağla
2. Yukarıdaki ayarları gir
3. Her push'ta otomatik deploy

**B) CLI ile:**
```bash
npm i -g netlify-cli
cd web
netlify init
netlify deploy --prod
```

### Dikkat Edilecekler
- `NEXT_PUBLIC_API_URL` production backend URL'ini göstermeli
- Netlify'da Next.js için `@netlify/plugin-nextjs` otomatik eklenir
- CORS: Backend'de `allow_origins` Netlify domain'ini içermeli

---

## 2. Backend — Render'a Deploy

### Gerekli Dosyalar

**`requirements.txt`** (zaten mevcut olmalı):
```
fastapi
uvicorn
twikit
openai
asyncpg
pydantic
langdetect
```

**`render.yaml`** (opsiyonel, Render Blueprint):
```yaml
services:
  - type: web
    name: kimbux-api
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn api:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: TWITTER_USERNAME
        sync: false
      - key: TWITTER_EMAIL
        sync: false
      - key: TWITTER_PASSWORD
        sync: false
      - key: OPENAI_API_KEY
        sync: false
      - key: DATABASE_URL
        sync: false
```

### Ortam Değişkenleri (Render Dashboard)

```
TWITTER_USERNAME=...
TWITTER_EMAIL=...
TWITTER_PASSWORD=...
OPENAI_API_KEY=...
DATABASE_URL=postgresql://...  (Neon Postgres URL)
```

### Deploy Adımları

1. Render.com → New → Web Service
2. GitHub repo bağla
3. Root directory: `.` (proje kökü)
4. Build: `pip install -r requirements.txt`
5. Start: `uvicorn api:app --host 0.0.0.0 --port $PORT`
6. Env vars ekle
7. Deploy

### Dikkat Edilecekler
- **cookies.json**: Render'da dosya sistemi geçici. İlk deploy'da login olacak, restart'ta cookie kaybolur → her restart'ta yeniden login
- **Free tier**: Render free tier 15dk inaktiviteden sonra uyur. İlk request ~30sn sürebilir
- **Rate limit**: Render'ın IP'si Twitter tarafından daha hızlı rate limit yiyebilir

---

## 3. Alternatif: Railway

Railway, Render'a benzer ama:
- Sleep yok (ücretli plan)
- Docker desteği daha iyi
- `railway up` CLI ile hızlı deploy

---

## 4. Production Kontrol Listesi

- [ ] Backend URL'i frontend env'e eklendi
- [ ] CORS ayarları production domain için güncellendi
- [ ] cookies.json .gitignore'da (commit edilmemeli!)
- [ ] .env .gitignore'da
- [ ] Database URL production Neon instance'ına işaret ediyor
- [ ] OpenAI API key production key kullanıyor
- [ ] Twitter credentials geçerli
- [ ] `npm run build` hatasız çalışıyor
- [ ] Backend health endpoint çalışıyor: `GET /api/health`
