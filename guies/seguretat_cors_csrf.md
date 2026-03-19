# Seguretat Web a fons: Entenent CORS i CSRF

**Resum:** Quan connectem un frontend independent (Vue) amb un backend (Django) apareixen mecanismes de seguretat integrats als navegadors web que ens poden bloquejar les peticions. Aquesta guia explica per què el teu navegador es queixa quan intentes fer una petició HTTP des de `localhost:5173` a `localhost:8000`, com el **CORS** ho soluciona, i què és el **CSRF** quan treballem amb APIs REST.

**Índex de continguts:**
* [1. L'origen del problema: La Same-Origin Policy (SOP)](#1-lorigen-del-problema-la-same-origin-policy-sop)
* [2. CORS: Donant permís al Frontend](#2-cors-donant-permís-al-frontend)
* [3. CSRF: Falsificació de peticions i APIs REST](#3-csrf-falsificació-de-peticions-i-apis-rest)

---

## 1. L'origen del problema: La Same-Origin Policy (SOP)

Els navegadors web (Chrome, Firefox, Safari) implementen una mesura de seguretat estricta anomenada **Same-Origin Policy (SOP)**. Aquesta política dicta que un codi JavaScript (el teu frontend) només pot fer peticions a un servidor si tots dos comparteixen exactament el mateix "Origen".

Un origen es defineix per la combinació de tres elements:
1.  **El protocol:** (ex: `http://` o `https://`)
2.  **El domini:** (ex: `localhost` o `app.com`)
3.  **El port:** (ex: `80`, `8000`, `5173`)

**Per què ens afecta a nosaltres?**
Durant el desenvolupament, el nostre frontend s'executa a `http://localhost:5173` i el backend a `http://localhost:8000`. Tot i ser la mateixa màquina, **el port és diferent**. Per tant, el navegador ho considera "Orígens Diferents" i, per defecte, bloqueja la lectura de les dades per protegir l'usuari d'atacs externs.

## 2. CORS: Donant permís al Frontend

Per solucionar el bloqueig de la SOP, existeix el **CORS (Cross-Origin Resource Sharing)**. És un mecanisme pel qual el servidor (Django) pot dir-li al navegador: *"Tranquil, conec aquest frontend i li dono permís per llegir les meves dades"*.

### Com ho implementem a Django?
A la plantilla base ja tens configurada la llibreria `django-cors-headers`. Aquesta eina intercepta les peticions i afegeix unes capçaleres (headers) especials a la resposta HTTP del backend. 

A l'arxiu `settings.py` hi trobaràs aquesta configuració:

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost", # Per a l'entorn Docker de producció
]
```

Amb això, quan el teu codi Vue faci una petició a Django, Django respondrà afegint la capçalera `Access-Control-Allow-Origin: http://localhost:5173`. El navegador ho llegirà, veurà que el servidor ho permet expressament, i deixarà passar les dades cap al teu codi JavaScript.

## 3. CSRF: Falsificació de peticions i APIs REST

El **CSRF (Cross-Site Request Forgery)** és un atac on un lloc web maliciós enganya el navegador de l'usuari perquè faci una acció no desitjada en una aplicació on ja està identificat (per exemple, esborrar el seu compte o fer una transferència). 

Tradicionalment, Django es protegeix d'això injectant un `csrfmiddlewaretoken` als formularis HTML i validant-lo en rebre un POST.

### Llavors, com gestionem el CSRF a la nostra API?

Quan treballem amb **Django REST Framework (DRF)** i un frontend separat com Vue, la gestió de la seguretat depèn del sistema d'autenticació que utilitzem:

* **Si fem servir Session Authentication (Galetes/Cookies):** El navegador envia automàticament la galeta de sessió en cada petició. En aquest cas, seríem vulnerables a CSRF i obligatòriament hauríem de configurar Vue perquè llegeixi el token CSRF i l'enviï a la capçalera `X-CSRFToken` en cada crida Axios.
* **Si fem servir Token Authentication o JWT (JSON Web Tokens):** Aquest és l'estàndard modern per a APIs REST (i el que s'acostuma a fer servir en aquests projectes). L'autenticació no va per galetes automàtiques, sinó que nosaltres afegim manualment el Token a la capçalera `Authorization` de cada petició Axios. 

**La clau:** Com que un atacant des d'una altra web no pot accedir a les dades locals del teu frontend (on guardem el JWT) i el navegador no l'envia sol, l'arquitectura basada en JWT és **immunitzada per naturalesa** contra atacs CSRF. Per això, quan es treballa exclusivament amb APIs i JWT, habitualment es relaxa la validació CSRF estricta als endpoints de l'API.
