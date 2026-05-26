# Scripts de proves creuades

Aquest paquet s'ha de descarregar i executar al vostre entorn. La part de codi s'ha d'organitzar obligatòriament dins una carpeta `test_session/`.

## 1. Estructura obligatòria

```text
test_session/
	docker-compose.tests.yml
	Dockerfile.tests
	sd2526_G1_G2.py
	sd2526_G1_G3.py
	output/
```

Notes:

1. Hi ha d'haver un script `sd2526_G1_Gx.py` per cada grup que s'avalua.
2. La carpeta `output/` es crea automàticament en executar les proves.
3. Aquesta carpeta `test_session/` s'ha d'adjuntar dins del repositori del grup com a part del lliurament.

## 2. Flux recomanat (sense instal·lar dependències locals)

Objectiu:

1. Definir un servei Docker per cada grup que s'avalua.
2. Mapejar a cada servei l'script adaptat (`sd2526_G1_G2.py`).
3. Guardar els resultats en fitxers dins `output/`.

La imatge de proves (`Dockerfile.tests`) porta les dependències preinstal·lades (`pytest`, `requests`, `pytest-html`) i també el **command integrat** per executar els tests. El servei només ha de mapar l'script adaptat a `/work/test_script.py`.

## 3. Preparació (descàrrega i adaptació)

1. Creeu una carpeta local anomenada `test_session/`.
2. Copieu-hi aquests fitxers base: `Dockerfile.tests` i `docker-compose.tests.yml`.
3. Creeu dins `test_session/` els scripts adaptats: `sd2526_G1_G2.py`, `sd2526_G1_G3.py`, etc.
4. Editeu `docker-compose.tests.yml` per afegir un servei per cada grup que avalueu.

## 4. Variables d'entorn suportades

L'script suporta:

- `BASE_API_URL` (prioritari)
- `BASE_URL` (fallback)

I també:

- `REGISTER_ENDPOINT`
- `LOGIN_ENDPOINT`
- `USERS_LIST_ENDPOINT`
- `USER_DETAIL_ENDPOINT_TEMPLATE`
- `EVENTS_ENDPOINT`
- `EVENT_DETAIL_ENDPOINT_TEMPLATE`
- `CHECKOUT_ENDPOINT`
- `ALLOW_NON_ADMIN_EVENT_CREATE`
- `ADMIN_USERNAME`
- `ADMIN_PASSWORD`

## 5. Com crear un servei per cada grup avaluat

Useu `docker-compose.tests.yml` com a base i afegiu un servei per cada script adaptat.

La plantilla ja inclou comentaris per guiar-vos. La mecanica recomanada es:

1. Duplicar el bloc d'un servei existent.
2. Canviar el nom del servei.
3. Canviar el fitxer mapejat (`./sd2526_G1_G2.py:/work/test_script.py:ro`).
4. Ajustar `TEST_ID` i `BASE_API_URL`.

Exemple de noms de servei:

- `tests_b01_c10`
- `tests_b01_d03`

Cada servei ha de:

1. Mapejar un fitxer adaptat concret (`sd2526_G1_G2.py`) a `/work/test_script.py`.
2. Mapejar `./output` a `/work/output` per recollir resultats.
3. Definir `TEST_ID` (per exemple `B01_C10`) per al nom dels fitxers de sortida.
4. Definir les variables d'entorn del grup que s'avalua, especialment `BASE_API_URL`.

Exemple de volum i variables en un servei:

```yaml
volumes:
	- ./sd2526_B01_C10.py:/work/test_script.py:ro
	- ./output:/work/output
environment:
	TEST_ID: B01_C10
	BASE_API_URL: http://host.docker.internal:8100
```

## 6. Execució

Des de dins `test_session/`:

```bash
docker compose -f docker-compose.tests.yml up --abort-on-container-exit
```

Per forçar reconstrucció de la imatge de proves:

```bash
docker compose -f docker-compose.tests.yml build --no-cache
```

Per aturar i netejar contenidors:

```bash
docker compose -f docker-compose.tests.yml down
```

## 7. Resultats esperats

A `output/` tindreu, per cada grup avaluat:

- un log de consola (`*.log`)
- un informe HTML (`*.html`)

Aquests fitxers es poden fer servir per omplir la taula de resultats de l'informe.

## 8. Adaptació per al lliurament

Cada grup ha d'adaptar l'script base i lliurar un fitxer per cada grup que s'avalua:

- `sd2526_G1_G2.py`

on:

- `G1`: codi del grup que avalua
- `G2`: codi del grup que s'avalua

Exemple:

- `sd2526_B01_C10.py`

I, a més, ha d'adjuntar la carpeta `test_session/` dins del seu repositori.
