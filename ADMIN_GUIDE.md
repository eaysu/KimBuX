# Admin Guide — KimBuX

## Cookie Management

### Problem
Render free tier'da dosya sistemi geçici — her restart'ta `cookies.json` silinir. Bu da her restart'ta Twitter'a yeniden login gerektir (~30sn gecikme).

### Çözüm: Cookie Import

Local'de geçerli bir `cookies.json` oluşturduktan sonra, bunu Render'a environment variable olarak ekleyebilirsin.

## Adım 1: Local'de Cookie Oluştur

```bash
# Backend'i local'de çalıştır
conda activate tw_env
uvicorn api:app --host 0.0.0.0 --port 5050

# Bir analiz yap (tarayıcıdan veya curl ile)
curl -X POST http://localhost:5050/api/analyze \
  -H 'Content-Type: application/json' \
  -d '{"username":"elonmusk","limit":100}'

# cookies.json otomatik oluşturuldu
```

## Adım 2: Cookie'yi Base64'e Encode Et

```bash
python admin_cookie_import.py
```

**Çıktı:**
```
✅ Cookies successfully encoded!

======================================================================
RENDER ENVIRONMENT VARIABLE
======================================================================

Key:   TWITTER_COOKIES_BASE64
Value: ewogICJfX2NmX2JtIjogIlo3dmdHNkNxN1RmWG1rTXJEajZ3RW5mN1BsUHEuZ1Rv...

======================================================================

Instructions:
1. Go to Render dashboard → Your service → Environment
2. Click 'Add Environment Variable'
3. Key: TWITTER_COOKIES_BASE64
4. Value: Copy the base64 string above
5. Save and redeploy
...
```

## Adım 3: Render'a Ekle

1. Render dashboard → **kimbux** service → **Environment**
2. **Add Environment Variable**
3. Key: `TWITTER_COOKIES_BASE64`
4. Value: (yukarıdaki base64 string'i yapıştır)
5. **Save**
6. **Manual Deploy** → **Deploy latest commit**

## Adım 4: Doğrula

Deploy bitince Render logs'unda:

```
✓ Loaded cookies from TWITTER_COOKIES_BASE64 env var
```

görmeli ve artık her restart'ta login gerekmemeli.

---

## Cookie Geçerliliği

Twitter cookies genellikle:
- **30-90 gün** geçerli
- IP değişikliğinde expire olabilir
- Şüpheli aktivitede Twitter tarafından iptal edilebilir

**Cookie expire olduğunda:**
1. Local'de yeni cookie oluştur (yukarıdaki adımlar)
2. `admin_cookie_import.py` ile yeni base64 al
3. Render'da `TWITTER_COOKIES_BASE64` değerini güncelle
4. Redeploy

---

## Database Temizleme

Negative cache veya eski analizleri temizlemek için:

```bash
conda activate tw_env

# Negative cache temizle
python -c "
import asyncio
from src.database import init_db, get_pool

async def clear():
    await init_db()
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute('DELETE FROM negative_cache')
        print('Negative cache cleared')
asyncio.run(clear())
"

# Tüm analizleri temizle (dikkatli!)
python -c "
import asyncio
from src.database import init_db, get_pool

async def clear():
    await init_db()
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute('DELETE FROM analyses')
        print('All analyses cleared')
asyncio.run(clear())
"
```

---

## Monitoring

### Render Logs

Render dashboard → **Logs** sekmesi:

- `✓ Loaded cookies from...` → Cookie başarılı
- `⚠ No cookies found, logging in...` → Fresh login
- `✗ Login failed...` → Credentials veya Twitter sorunu
- `INFO: ... 200 OK` → Başarılı request
- `INFO: ... 404 Not Found` → Kullanıcı bulunamadı
- `INFO: ... 500 Internal Server Error` → Backend hatası

### Database Stats

```bash
conda activate tw_env
python -c "
import asyncio
from src.database import init_db, get_pool

async def stats():
    await init_db()
    pool = await get_pool()
    async with pool.acquire() as conn:
        analyses = await conn.fetchval('SELECT COUNT(*) FROM analyses')
        neg_cache = await conn.fetchval('SELECT COUNT(*) FROM negative_cache')
        print(f'Total analyses: {analyses}')
        print(f'Negative cache entries: {neg_cache}')
asyncio.run(stats())
"
```
