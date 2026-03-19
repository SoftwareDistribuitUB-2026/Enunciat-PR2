# Base de dades amb Django: Models, Relacions i Migracions

**Resum:** Aquesta guia explica com Django interactua amb la base de dades a través del seu ORM (Object-Relational Mapper). Aprendràs què és un Model, quins tipus de camps i relacions existeixen, com utilitzar el gestor d'objectes per fer consultes, què són els senyals (signals) per reaccionar a canvis, i com aplicar les migracions per actualitzar l'esquema de la base de dades.

**Índex de continguts:**
* [1. Què és un Model i l'ORM?](#1-què-és-un-model-i-lorm)
* [2. Camps principals i Relacions](#2-camps-principals-i-relacions)
* [3. El Gestor d'Objectes (Manager)](#3-el-gestor-dobjectes-manager)
* [4. Senyals (Signals)](#4-senyals-signals)
* [5. Migracions: makemigrations i migrate](#5-migracions-makemigrations-i-migrate)
* [6. Recursos i Documentació](#6-recursos-i-documentació)

---

## 1. Què és un Model i l'ORM?

A Django, no escrivim consultes SQL manualment (`SELECT * FROM usuaris`). Utilitzem l'**ORM**, que ens permet definir l'estructura de la nostra base de dades utilitzant classes de Python (Models). Cada classe equivalent a una taula, i cada atribut de la classe és una columna.

## 2. Camps principals i Relacions

Els models es defineixen al fitxer `models.py` de la teva aplicació. Django ofereix tipus de camps per a gairebé qualsevol necessitat:

* `CharField(max_length=...)`: Per a textos curts.
* `TextField()`: Per a textos llargs.
* `IntegerField()` / `FloatField()`: Per a números.
* `DateTimeField(auto_now_add=True)`: Per a dates i hores.
* `BooleanField(default=False)`: Per a valors Cert/Fals.

**Relacions entre models:**
Les bases de dades relacionals brillen quan connectem taules. Django ho fa molt senzill:
* **1 a N (Una a Moltes):** Utilitzem `ForeignKey`. Per exemple, un Article pertany a un Autor, però un Autor pot tenir molts Articles.
* **N a M (Moltes a Moltes):** Utilitzem `ManyToManyField`. Per exemple, un Estudiant pot estar matriculat a moltes Assignatures, i una Assignatura té molts Estudiants.
* **1 a 1:** Utilitzem `OneToOneField`. Útil per estendre models, com crear un `PerfilUsuari` associat exclusivament a un `User`.

## 3. El Gestor d'Objectes (Manager)

Cada model de Django té un gestor per defecte anomenat `objects`. S'utilitza per interactuar amb la base de dades:

* Llegir tots: `Article.objects.all()`
* Filtrar: `Article.objects.filter(publicat=True)`
* Obtenir-ne un (o fallar): `Article.objects.get(id=1)`
* Crear: `Article.objects.create(titol="Nou")`

## 4. Senyals (Signals)

Els senyals permeten executar codi automàticament quan passen certes coses a la base de dades. Els més comuns són `pre_save` i `post_save`. 
Per exemple, pots utilitzar un senyal `post_save` associat al model `User` perquè, cada vegada que es creï un usuari nou a la base de dades, es creï automàticament el seu perfil associat, sense haver de recordar-te de programar-ho a cada controlador.

## 5. Migracions: makemigrations i migrate

Quan modifiques un fitxer `models.py` (creant models nous o canviant camps), la base de dades real encara no ho sap. Cal sincronitzar-los en dos passos:

1. **Crear les migracions (`makemigrations`):**
   ```bash
   uv run python manage.py makemigrations
   ```
   Això llegeix els teus models i crea un fitxer Python amb les instruccions per alterar la base de dades.
   
2. **Aplicar les migracions (`migrate`):**
   ```bash
   uv run python manage.py migrate
   ```
   Això executa els fitxers creats al pas anterior i modifica finalment l'esquema de la base de dades (SQLite o MariaDB).

## 6. Recursos i Documentació
Per aprofundir, consulta la documentació oficial:
* [Introducció als Models de Django](https://docs.djangoproject.com/en/stable/topics/db/models/)
* [QuerySets (Com fer consultes)](https://docs.djangoproject.com/en/stable/topics/db/queries/)
