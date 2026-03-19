Tens tota la raó. Has tocat el cor de la qüestió: no podem assumir que tothom domina el cicle de vida de les dades (Models) ni la seva exposició (DRF) abans d'arribar a l'autenticació. Aquestes guies són fonamentals perquè els estudiants tinguin una referència clara on recórrer.

Com que són temes densos i volem mantenir la qualitat i claredat, et proposo **redactar ara les dues primeres guies (Models de Django i Creació d'APIs amb DRF)**. Així les deixem tancades i, en el següent pas, ataquem exclusivament la guia de Seguretat/JWT, que requereix unir el món del backend i del frontend amb molt de detall.

Aquí tens les dues primeres guies estructurades.

---

### Fitxer: `guies/django_models_orm.md`

```markdown
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

1. **Crear els plànols (`makemigrations`):**
   ```bash
   uv run python manage.py makemigrations
   ```
   Això llegeix els teus models i crea un fitxer Python amb les instruccions per alterar la base de dades.
   
2. **Aplicar els plànols (`migrate`):**
   ```bash
   uv run python manage.py migrate
   ```
   Això executa els fitxers creats al pas anterior i modifica finalment l'esquema de la base de dades (SQLite o MariaDB).

## 6. Recursos i Documentació
Per aprofundir, consulta la documentació oficial:
* [Introducció als Models de Django](https://docs.djangoproject.com/en/stable/topics/db/models/)
* [QuerySets (Com fer consultes)](https://docs.djangoproject.com/en/stable/topics/db/queries/)
```


# Creació d'APIs REST amb Django REST Framework (DRF)

**Resum:** Tenir les dades a la base de dades està bé, però el nostre Frontend (Vue) necessita llegir-les. Aquesta guia explica com transformar els nostres Models de Django en una API REST utilitzant DRF. Repassarem els estàndards de comunicació HTTP i l'arquitectura de DRF basada en Serialitzadors, Vistes (ViewSets) i Enrutadors (Routers).

**Índex de continguts:**
* [1. Bones pràctiques: Mètodes HTTP i Codis d'Estat](#1-bones-pràctiques-mètodes-http-i-codis-destat)
* [2. Serialitzadors (Serializers)](#2-serialitzadors-serializers)
* [3. ViewSets (Controladors)](#3-viewsets-controladors)
* [4. Routers (Enrutadors URL)](#4-routers-enrutadors-url)
* [5. Recursos i Documentació](#5-recursos-i-documentació)

---

## 1. Bones pràctiques: Mètodes HTTP i Codis d'Estat

Una API REST és un estàndard de comunicació. Vue farà peticions a URLs específiques utilitzant **Mètodes HTTP** per indicar la intenció, i Django respondrà amb **Codis d'Estat** per indicar el resultat.

**Mètodes HTTP principals:**
* `GET`: Llegir dades (Llistar tots o obtenir-ne un).
* `POST`: Crear un recurs nou.
* `PUT` / `PATCH`: Actualitzar un recurs existent.
* `DELETE`: Esborrar un recurs.

**Codis d'Estat (Respostes del Backend):**
* `200 OK` / `201 Created`: Tot ha anat bé.
* `400 Bad Request`: El Frontend ha enviat dades invàlides (ex. falta un camp obligatori).
* `401 Unauthorized`: Cal iniciar sessió per fer això.
* `403 Forbidden`: Tens sessió iniciada, però no tens permís per a aquesta acció.
* `404 Not Found`: El recurs no existeix.

## 2. Serialitzadors (Serializers)

El Frontend "parla" en format JSON. La base de dades de Django "parla" en objectes Python. Els **Serialitzadors** són els traductors oficials.
Tenen dues funcions:
1. Agafar un model de la base de dades i convertir-lo a JSON (per enviar-lo amb un GET).
2. Agafar un JSON entrant, validar-lo, i convertir-lo a un model (per guardar-lo en un POST).

A DRF utilitzem generalment `ModelSerializer`, que fa tota la feina automàticament a partir d'un model existent:

```python
from rest_framework import serializers
from .models import Article

class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['id', 'titol', 'contingut', 'publicat'] # Camps que s'exposaran
```

## 3. ViewSets (Controladors)

Mentre que a Django clàssic hauríem de fer una funció per al GET, una altra per al POST, etc., DRF ens ofereix els `ModelViewSet`. Aquest component agafa el nostre Serialitzador, la nostra base de dades (`queryset`) i **genera automàticament tota la lògica per a les 5 operacions clàssiques** (Llistar, Crear, Recuperar un, Actualitzar i Esborrar).

```python
from rest_framework import viewsets
from .models import Article
from .serializers import ArticleSerializer

class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
```

## 4. Routers (Enrutadors URL)

Per connectar el ViewSet a una URL (ex: `/api/articles/`), utilitzem un **Router**. El Router llegeix el ViewSet i crea automàticament totes les rutes (`GET /api/articles/`, `POST /api/articles/`, `GET /api/articles/1/`, etc.) sense que les hàgim de definir una a una al fitxer `urls.py`.

```python
from rest_framework.routers import DefaultRouter
from .views import ArticleViewSet

router = DefaultRouter()
router.register(r'articles', ArticleViewSet)

urlpatterns = router.urls
```

## 5. Recursos i Documentació
Per aprofundir en qualsevol d'aquests conceptes, revisa la documentació oficial de DRF:
* [Django REST Framework - Tutorial Quickstart](https://www.django-rest-framework.org/tutorial/quickstart/)
* [Serializers](https://www.django-rest-framework.org/api-guide/serializers/)
* [ViewSets i Routers](https://www.django-rest-framework.org/api-guide/viewsets/)
