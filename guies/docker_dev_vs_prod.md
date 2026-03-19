# Entorns d'Execució: Desenvolupament vs Producció (Docker)

**Resum:** Aquesta guia explica la diferència fonamental entre com executarem l'aplicació mentre la programem (entorn local de desenvolupament) i com es desplegaria en un servidor real (entorn de producció amb Docker). Aprendràs per què necessitem eines diferents per a cada fase, com configurar les variables d'entorn amb un fitxer `.env` i quines comandes utilitzar per orquestrar tota la infraestructura final (Frontend, Backend, Base de Dades i Enrutador) amb un sol clic mitjançant Docker Compose.

**Índex de continguts:**
* [1. Dos entorns, dos objectius](#1-dos-entorns-dos-objectius)
* [2. L'Entorn de Desenvolupament (El teu dia a dia)](#2-lentorn-de-desenvolupament-el-teu-dia-a-dia)
* [3. L'Entorn de Producció (Docker)](#3-lentorn-de-producció-docker)
* [4. Configuració: El fitxer `.env`](#4-configuració-el-fitxer-env)
* [5. Com aixecar l'entorn de producció](#5-com-aixecar-lentorn-de-producció)

---

## 1. Dos entorns, dos objectius

Quan creem programari distribuït, no utilitzem les mateixes eines mentre estem picant codi que quan l'aplicació està acabada i donant servei a milers d'usuaris. 

* **Desenvolupament:** Prioritza la velocitat del programador. Volem que si canviem una línia de codi, s'actualitzi a l'instant al navegador (*Hot Reloading*), i preferim bases de dades lleugeres que no requereixin instal·lació complexa.
* **Producció:** Prioritza l'estabilitat, la seguretat i el rendiment. El codi ja no canvia en temps real, necessitem servidors web ràpids, bases de dades robustes i aïllament entre els diferents serveis.

## 2. L'Entorn de Desenvolupament (El teu dia a dia)

Mentre estiguis treballant a les sessions pràctiques, treballaràs principalment en aquest mode. 

* **Backend:** Utilitzaràs el servidor integrat de Django (`uv run python manage.py runserver`) i una base de dades local **SQLite**.
* **Frontend:** Utilitzaràs el servidor de Vite (`npm run dev`), que compila els fitxers de Vue al vol i actualitza el navegador a l'instant.

Són dos processos totalment independents executant-se a la teva màquina (normalment als ports `8000` i `5173`).

## 3. L'Entorn de Producció (Docker)

Quan vulguem simular un desplegament real (o quan l'assignatura ho requereixi), utilitzarem **Docker Compose**. Aquest sistema llegeix el fitxer `docker-compose.yml` que tens a l'arrel de la plantilla i aixeca 4 "contenidors" (màquines virtuals lleugeres) interconnectats:

1.  **Traefik (Reverse Proxy):** Actua com a porta d'entrada única (Port 80). Si entres a `http://localhost/api`, envia la petició al Backend. Si entres a `http://localhost/`, l'envia al Frontend.
2.  **Base de Dades (MariaDB):** Substitueix SQLite per un motor relacional de grau industrial.
3.  **Backend (Django + Gunicorn):** El teu codi de Python s'executa ara a través de Gunicorn, un servidor preparat per rebre múltiples peticions simultànies i parlar amb MariaDB.
4.  **Frontend (Vue + Nginx):** El teu codi de Vue ja no s'executa amb Node.js. S'ha "construït" prèviament convertint-se en HTML/JS pur i es serveix a través de Nginx, un dels servidors web més ràpids del món.

## 4. Configuració: El fitxer `.env`

A producció, no podem tenir contrasenyes ni dominis escrits directament al codi font. S'utilitzen **Variables d'Entorn**. 

Al repositori del codi base trobaràs un fitxer anomenat `env_sample`.
1. Fes-ne una còpia al mateix directori arrel i anomena'l **`.env`** (assegura't que el punt inicial hi és).
2. Obre'l i revisa'l. Aquest fitxer conté el domini de l'aplicació (`DOMAIN=localhost`) i les credencials de la base de dades.
3. *Nota de seguretat:* El fitxer `.env` està ignorat per Git (`.gitignore`). Mai, **mai**, s'ha de pujar a un repositori públic, ja que conté secrets!

## 5. Com aixecar l'entorn de producció

Un cop tinguis el fitxer `.env` creat, obre una terminal a l'arrel del teu projecte i executa:

```bash
docker compose up --build
```

* L'opció `--build` obliga a Docker a llegir els fitxers `Dockerfile` de les carpetes frontend i backend i construir les imatges des de zero, assegurant que s'inclouen els teus últims canvis de codi.
* *Nota:* La primera vegada que l'executis, trigarà una mica perquè ha de descarregar les imatges base de Node, Python, Traefik i MariaDB.

Quan la consola deixi de moure's i vegis que els serveis estan llestos, obre el teu navegador i ves simplement a:

👉 **http://localhost**

Ja no et cal posar cap port. Traefik rebrà la teva petició i farà la màgia. Per aturar tota la infraestructura, prem `Ctrl+C` a la terminal, o executa `docker compose down` si ho tenies corrent en segon pla (afegint l'opció `-d` a la comanda inicial).
