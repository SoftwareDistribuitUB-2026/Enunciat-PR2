# Docker Desktop a Windows (Aules)

**Resum:** Aquesta mini guia explica com comprovar Docker Desktop a les aules Windows i fer una prova de xarxa amb un `docker compose` senzill (`traefik + nginx`) accessible des d'altres màquines de la mateixa xarxa.

**Índex de continguts:**
* [1. Posada en marxa a l'aula](#1-posada-en-marxa-a-laula)
* [2. Prova ràpida: compose amb Traefik i Nginx](#2-prova-ràpida-compose-amb-traefik-i-nginx)
* [3. Trobar la IP de Windows](#3-trobar-la-ip-de-windows)
* [4. Verificar accés des d'altres màquines](#4-verificar-accés-des-daltres-màquines)

---

## 1. Posada en marxa a l'aula

1. A les aules, arrencant en Windows, hauríeu de trobar l'aplicació **Docker Desktop** instal·lada.
2. Arranqueu Docker Desktop i espereu que indiqui que el motor està actiu (Docker Engine running).
3. Obriu un terminal. Podeu fer servir:
  * PowerShell o CMD de Windows.
  * El terminal integrat del mateix Docker Desktop (opció recomanada si ja el teniu obert).
4. Comproveu que Docker funciona:

```powershell
docker version
docker compose version
```

Si aquestes comandes responen correctament, ja podeu utilitzar comandes Docker amb normalitat.

## 2. Prova ràpida: compose amb Traefik i Nginx

Creeu una carpeta buida i, dins, un fitxer `compose.yml` amb aquest contingut:

```yaml
services:
  traefik:
    image: traefik:v3.0
    command:
      - --providers.docker=true
      - --providers.docker.exposedbydefault=false
      - --entrypoints.web.address=:80
    ports:
      - "80:80"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro

  web:
    image: nginx:alpine
    labels:
      - traefik.enable=true
      - traefik.http.routers.web.rule=PathPrefix(`/`)
      - traefik.http.routers.web.entrypoints=web
      - traefik.http.services.web.loadbalancer.server.port=80
```

A la mateixa carpeta, executeu:

```powershell
docker compose up -d
```

Comprovació local al mateix PC:

```powershell
curl http://localhost
```

També ho podeu obrir al navegador: `http://localhost`.

## 3. Trobar la IP de Windows

Per accedir des d'altres màquines de l'aula, necessiteu la IP local del PC on corre Docker Desktop.

Comanda recomanada:

```powershell
ipconfig
```

Busqueu la interfície de xarxa activa (Ethernet o Wi-Fi) i anoteu el camp **IPv4 Address** (per exemple `192.168.1.34`).

## 4. Verificar accés des d'altres màquines

1. Des d'un altre ordinador de la mateixa xarxa, obriu:
   `http://IP_DEL_PC_WINDOWS`
   Exemple: `http://192.168.1.34`
2. Si no respon:
   * Comproveu que els dos equips són a la mateixa xarxa.
   * Reviseu el tallafoc de Windows i permeteu connexions entrants al port `80` en xarxa privada.
   * Verifiqueu que els contenidors estan actius amb `docker compose ps`.

Per aturar la prova:

```powershell
docker compose down
```
