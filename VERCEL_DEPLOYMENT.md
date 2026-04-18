# Vercel Deployment Guide - Unified Frontend + Backend

Ez az útmutató segít a Reflektor alkalmazás Vercelen történő telepítésében, ahol a frontend és backend egyetlen URL-ről érhető el.

## Hogyan működik?

A Vercel serverless funkcióit használjuk:
- **Frontend**: Static React alkalmazás (build-elve)
- **Backend**: Serverless Python funkciók (`/api/*` útvonalakon)
- **Egyetlen domain**: Minden a `https://yourdomain.vercel.app` címről elérhető

## Telepítés lépései

### 1. Repository előkészítése

Győződj meg róla, hogy a repository-d tartalmazza:
- `frontend/` mappa a React alkalmazással
- `api/` mappa a serverless funkciókkal
- `vercel.json` konfigurációs fájl
- `requirements-vercel.txt` Python dependenciák

### 2. Vercel projekt beállítása

1. **Lépj be a Vercel dashboard-be**: [vercel.com](https://vercel.com)
2. **Import GitHub repository**: Add hozzá a repository-d
3. **Framework preset**: Válaszd a "Other" opciót
4. **Build settings**:
   - **Build Command**: `cd frontend && npm run build`
   - **Output Directory**: `frontend/dist`
   - **Install Command**: `cd frontend && npm install`

### 3. Environment Variables beállítása

A Vercel projekt beállításainál add hozzá ezeket:

```
OPENAI_API_KEY=sk-your-actual-openai-key-here
OPENAI_MODEL=gpt-4o
PYTHON_VERSION=3.11
```

### 4. Deployment

1. **Commit és push** a változtatásokat a GitHub-ba
2. Vercel automatikusan elindítja a build-et
3. Várj a deployment befejezésére

## URL struktúra

Deployment után az alábbi URL-ek lesznek elérhetők:

- **Frontend**: `https://yourdomain.vercel.app/`
- **API Health**: `https://yourdomain.vercel.app/api/health`
- **Create Session**: `https://yourdomain.vercel.app/api/sessions`
- **API Documentation**: `https://yourdomain.vercel.app/api/docs`

## Tesztelés

### 1. Health check
```bash
curl https://yourdomain.vercel.app/api/health
```

### 2. Session létrehozás
```bash
curl -X POST https://yourdomain.vercel.app/api/sessions
```

## Hibaelhárítás

### Gyakori problémák:

1. **CORS hiba**: A serverless funkcióknak be van állítva a CORS
2. **API kulcs hiba**: Ellenőrizd az environment variables-t
3. **Build hiba**: Ellenőrizd a `frontend/package.json`-t
4. **Python hiba**: Ellenőrizd a `requirements-vercel.txt`-t

### Logok megtekintése:
1. Vercel dashboard → Functions → View Logs
2. Vercel CLI: `vercel logs`

## Domain beállítása

Saját domainhez:

1. **Vercel dashboard → Domains → Add**
2. **Add domain**: Add a saját domain-edet
3. **DNS beállítások**: Vercel megadja a szükséges DNS rekordokat
4. **SSL**: Vercel automatikusan beállítja az SSL-t

## Költségek

- **Hobby tier**: Ingyenes
- **Function calls**: 100GB/hó (ingyenes)
- **Bandwidth**: 100GB/hó (ingyenes)
- **Build minutes**: 300 perc/hó (ingyenes)

Kisebb projektekhez ez teljesen ingyenes.

## Performance optimalizálás

1. **Edge functions**: Globális gyorsítótár
2. **Static assets**: Vercel CDN
3. **Function caching**: Response cache beállítása

## Monitorozás

- Vercel Analytics: Látogatottság
- Vercel Speed: Performance metrikák
- Function logs: API hívások

## Skálázás

Nagyobb forgalom esetén:
- Pro plan: Korlátlan function calls
- Enterprise: Dedikált infrastruktúra

## Összefoglalás

Ezzel a konfigurációval:
- ✅ Egyetlen URL-ről érhető el minden
- ✅ Automatikus SSL és CDN
- ✅ Ingyenes a kis forgalomhoz
- ✅ Globális gyorsítótár
- ✅ Egyszerű deployment
