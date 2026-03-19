# Tasques Asíncrones i Programades a Django

**Resum:** En aplicacions web, algunes accions triguen massa a executar-se (com enviar desenes de correus electrònics) o s'han d'executar automàticament cada cert temps (com aplicar descomptes a mitjanit). Si fem això dins d'una petició HTTP normal, el navegador de l'usuari es quedarà penjat esperant. Aquesta guia t'explica com utilitzar el sistema de tasques en segon pla de Django per resoldre aquest problema, i com escalar cap a eines com Celery i Redis quan el projecte creix.

**Índex de continguts:**
* [1. El problema: El coll d'ampolla HTTP](#1-el-problema-el-coll-dampolla-http)
* [2. Tasques en segon pla amb Django (Natiu)](#2-tasques-en-segon-pla-amb-django-natiu)
* [3. Tasques programades (Cron Jobs)](#3-tasques-programades-cron-jobs)
* [4. Ecosistema Avançat: Celery i Redis](#4-ecosistema-avançat-celery-i-redis)
* [5. Referències i Enllaços Útils](#5-referències-i-enllaços-útils)

---

## 1. El problema: El coll d'ampolla HTTP

Quan un usuari fa clic a "Comprar" i el frontend envia una petició `POST` al backend, el servidor Django ha de fer diverses coses: validar les dades, guardar-les a la base de dades, connectar-se a una passarel·la de pagament, generar un PDF amb l'entrada i enviar un correu electrònic.

Si tot això es fa de manera **síncrona** (línia a línia), l'usuari pot estar 5 o 10 segons veient un icona de càrrega. Si mil usuaris ho fan alhora, el servidor col·lapsarà. 
La solució és fer només el més ràpid i crític (guardar la compra) de forma síncrona i enviar el procés de generar el PDF i el correu a una **cua de tasques asíncrones**.

## 2. Tasques en segon pla amb Django (Natiu)

A partir de Django 6, el framework inclou suport natiu per a l'execució de tasques en segon pla utilitzant la mateixa base de dades del projecte com a cua de missatges (ideal per a desenvolupament i projectes de mida mitjana).

Per definir una tasca que s'ha d'executar fora del cicle HTTP, utilitzem un decorador especial (consulta la documentació oficial per veure la sintaxi exacta de la versió que estem utilitzant). Quan crides aquesta funció des del teu ViewSet, en lloc d'executar-se al moment, s'afegeix a una taula de la base de dades. 

Un procés separat (un *worker* que aixequem a la terminal amb una comanda de `manage.py`) anirà llegint aquesta taula i executant les tasques una per una en segon pla.

## 3. Tasques programades (Cron Jobs)

Un altre cas d'ús molt comú són les tasques que no depenen del clic d'un usuari, sinó del temps. En el nostre projecte, podríem voler un procés que s'executi cada nit a les 00:00h per buscar esdeveniments propers amb poques vendes i aplicar-los un descompte (Preus Dinàmics).

Amb el gestor natiu, pots programar que una tasca s'afegeixi a la cua periòdicament utilitzant expressions CRON (ex: `0 0 * * *` per executar-se cada mitjanit).

## 4. Ecosistema Avançat: Celery i Redis

Si la teva aplicació creix molt i necessites executar milers de tasques per segon, utilitzar la base de dades relacional com a cua generarà problemes de rendiment. A la indústria, l'estàndard és utilitzar **Celery** juntament amb **Redis**.

* **Redis:** És una base de dades ultraràpida que funciona en memòria RAM (actua com a bústia de missatges, o *Broker*).
* **Celery:** És el programa (*Worker*) que llegeix els missatges de Redis i executa el codi Python.

**Com integrar-ho (Nivell Pro):**
Si vols implementar això a la teva pràctica, hauràs de modificar la infraestructura:

1. **Afegir Redis a Docker:** Modificar l'arxiu `docker-compose.yml` per afegir un nou servei:
   ```yaml
   redis:
     image: redis:alpine
     ports:
       - "6379:6379"
   ```
2. **Instal·lar llibreries:** Afegir `celery` i `redis` a les dependències del backend.
3. **Configurar Django:** Indicar a `settings.py` que el *Broker URL* ara apunta a `redis://redis:6379/0`.
4. **Aixecar el Worker:** Afegir un altre servei al `docker-compose.yml` que executi la comanda `celery -A nom_projecte worker --loglevel=info` en lloc del servidor web tradicional.

## 5. Referències i Enllaços Útils
* [Documentació Oficial de Django - Background Tasks](https://docs.djangoproject.com/en/stable/topics/async/) *(Nota: Revisa l'apartat específic de cues de la teva versió)*
* [Celery Project - First Steps with Django](https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html)
* [Redis Official Image - Docker Hub](https://hub.docker.com/_/redis)
