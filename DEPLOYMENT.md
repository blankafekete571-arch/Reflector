# Reflektor Deployment Guide

Ez az útmutató segít a Reflektor alkalmazás teljesen ingyenesen történő telepítésében a saját domaineden.

## Ingyenes Deployment Opciók

### 1. Docker Compose (VPS/Cloud Server)

**Előfeltételek:**
- VPS vagy cloud server (pl. Oracle Cloud Free Tier, AWS Free Tier)
- Docker és Docker Compose telepítve
- Domain név

**Lépések:**

1. **Klónozd a repository-t:**
```bash
git clone <repository-url>
cd Reflector-develop
```

2. **Állítsd be a környezeti változókat:**
```bash
cp .env.example .env
# Szerkeszd a .env fájlt az OpenAI API kulccsal
```

3. **Építsd és indítsd a containereket:**
```bash
docker-compose up -d
```

4. **Ellenőrizd az állapotot:**
```bash
docker-compose ps
curl http://localhost:8000/health
```

### 2. Render.com (Teljesen ingyenes)

**Backend Deployment:**
1. Hozz létre egy új Web Service-et
2. Kösd össze a GitHub repository-dal
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `uvicorn navigate:app --host 0.0.0.0 --port $PORT`
5. Environment Variables:
   - `OPENAI_API_KEY`: a te OpenAI kulcsod
   - `PYTHON_VERSION`: `3.11.0`

**Frontend Deployment:**
1. Hozz létre egy új Static Site-ot
2. Kösd össze a frontend mappával
3. Build Command: `npm run build`
4. Publish Directory: `dist`
5. Add hozzá a backend URL-t a VITE_API_URL environment variable-ben

### 3. Railway.app (Ingyenes tier)

1. Hozz létre egy új projectet
2. Importáld a GitHub repository-t
3. Railway automatikusan felismeri a Python/Node.js alkalmazást
4. Add hozzá az environment variable-eket

### 4. Vercel + PythonAnywhere

**Frontend (Vercel):**
1. Hozz létre új projectet a Vercelen
2. Importáld a frontend mappát
3. Build Command: `npm run build`
4. Output Directory: `dist`

**Backend (PythonAnywhere):**
1. Hozz létre ingyenes fiókot
2. Töltsd fel a fájlokat
3. Telepítsd a dependenciákat: `pip install -r requirements.txt`
4. Indítsd a WSGI alkalmazást

## Domain Konfiguráció

Miután telepítetted az alkalmazást:

1. **DNS beállítások:**
   - `A record`: `yourdomain.com` → a szerver IP címe
   - `CNAME record`: `www` → `yourdomain.com`

2. **HTTPS beállítás:**
   - Használj Let's Encrypt tanúsítványt
   - Vagy a hosting szolgáltatás beépített SSLjét

## Környezeti Változók

**Szükséges environment variable-ek:**
- `OPENAI_API_KEY`: OpenAI API kulcs
- `OPENAI_MODEL`: `gpt-4o` (alapértelmezett)

## Monitoring

**Health check endpoint:**
- `GET /health` - visszaadja a szerver állapotát

**Logok:**
- Backend: `backend_stdout.log`, `backend_stderr.log`
- Frontend: Nginx access/error logok

## Hibaelhárítás

**Gyakori problémák:**
1. **CORS hibák**: Ellenőrizd a CORS beállításokat a backendben
2. **API kulcs hiba**: Győződj meg róla, hogy az `OPENAI_API_KEY` helyesen van beállítva
3. **Port hibák**: Ellenőrizd, hogy a portok szabadok-e
4. **Build hibák**: Ellenőrizd a dependenciákat és a build parancsokat

## Skálázhatóság

Az ingyenes tier-ek korlátozott erőforrásokkal rendelkeznek:
- Render: 750 óra/hó
- Railway: $5 kredit/hó
- PythonAnywhere: 1 web app

Nagyobb forgalom esetén érdemes fizetős plan-re váltani.
