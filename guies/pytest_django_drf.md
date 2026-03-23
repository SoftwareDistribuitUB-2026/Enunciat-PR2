# Provant el codi amb `pytest` i Django REST Framework

**Resum:**
En aquesta guia aprendrem a utilitzar `pytest`, l'estàndard actual per a la creació de proves en Python. Deixarem enrere les eines per defecte per adoptar una sintaxi més neta i potent. Explorarem com configurar l'entorn, com controlar el cicle de vida de les proves (pre i post execució), com agrupar-les en *suites*, forçar-ne l'ordre, provar excepcions, simular usuaris autenticats i, finalment, com mesurar quina part del nostre codi està realment coberta per les proves.

**Índex de continguts:**
1. L'entorn bàsic: *Fixtures* a `conftest.py`
2. La nostra primera prova amb `pytest`
3. Pre-proves i Post-proves: El cicle de vida amb `yield`
4. *Suites* de proves i ordre d'execució
5. Provant l'inesperat: Com capturar excepcions
6. Simulant l'autenticació a l'API
7. Cobertura de codi (*Code Coverage*)
8. Referències

---

#### 1. L'entorn bàsic: *Fixtures* a `conftest.py`
A diferència de les proves tradicionals orientades a objectes que utilitzen mètodes opacs d'inicialització, `pytest` utilitza **fixtures**: peces de codi reutilitzables que s'injecten allà on es necessiten. 

Per treballar de forma òptima amb DRF, creem un fitxer anomenat `conftest.py` dins la carpeta `backend/api/tests/`. Aquest fitxer guarda les *fixtures* globals per a tot el projecte.

```python
# backend/api/tests/conftest.py
import pytest
from rest_framework.test import APIClient

@pytest.fixture
def api_client():
    """Inicialitza i retorna el client de proves de DRF."""
    return APIClient()
```

#### 2. La nostra primera prova amb `pytest`
Reescrivim la prova del model `User` amb la sintaxi nativa de Python. L'etiqueta `@pytest.mark.django_db` és obligatòria per donar permís a la prova per accedir a la base de dades (i assegurar que s'esborri tot al final).

```python
# backend/api/tests/test_users.py
import pytest
from django.contrib.auth.models import User
from rest_framework import status

@pytest.mark.django_db
def test_create_user(api_client):
    url = '/api/v1/users/'
    data = {'username': 'testuser', 'password': 'testpassword123'}
    
    response = api_client.post(url, data, format='json')
    
    assert response.status_code == status.HTTP_201_CREATED
    assert User.objects.count() == 1
```

#### 3. Pre-proves i Post-proves: El cicle de vida amb `yield`
A vegades necessitem preparar dades abans d'una prova (Setup) i netejar-les un cop ha acabat (Teardown). A `pytest`, això es fa de manera molt elegant dins de les mateixes *fixtures* utilitzant la paraula clau `yield` en lloc de `return`.

```python
@pytest.fixture
def fitxer_temporal():
    # SETUP (Pre-prova): Es fa abans d'executar el test
    arxiu = open("test_temp.txt", "w")
    arxiu.write("Dades de prova")
    
    yield arxiu # Aquí s'atura la fixture i s'executa el test
    
    # TEARDOWN (Post-prova): Es fa un cop el test ha acabat
    arxiu.close()
    import os
    os.remove("test_temp.txt")
```

#### 4. *Suites* de proves i ordre d'execució
Una *suite* de proves és simplement una agrupació lògica de proves relacionades. A `pytest`, ho fem agrupant funcions dins d'una classe (sense necessitat d'heretar de res especial).

D'altra banda, **la regla d'or del testing és que les proves han de ser independents**. No obstant això, en proves d'integració complexes, a vegades necessitem forçar un ordre. Això s'aconsegueix amb el connector `pytest-order` i l'etiqueta `@pytest.mark.order`.

```python
import pytest

class TestFluxDeCompra: # Això és una Suite de proves
    
    @pytest.mark.order(1)
    def test_crear_carret(self):
        assert True

    @pytest.mark.order(2)
    def test_afegir_producte(self):
        # Aquest test s'executarà sempre després del número 1
        assert True
```

#### 5. Provant l'inesperat: Com capturar excepcions
No només hem de provar el camí feliç; també hem de verificar que el nostre codi falla quan toca i llença les excepcions correctes. Ho fem amb el bloc `with pytest.raises()`.

```python
import pytest
from django.core.exceptions import ValidationError
from api.models import Event

@pytest.mark.django_db
def test_event_sense_titol_falla():
    event = Event(descripcio="Descripció", capacitat_maxima=100)
    
    # Comprovem que en intentar validar-lo (full_clean) salta l'error esperat
    with pytest.raises(ValidationError):
        event.full_clean()
```
*Nota: Quan provem l'API directament amb `api_client`, DRF sol capturar l'excepció i retornar un codi HTTP 400 Bad Request, de manera que comprovaríem l'`assert response.status_code == 400` en lloc de l'excepció pura.*

#### 6. Simulant l'autenticació a l'API
La majoria d'APIs reals estan protegides. Per provar un *endpoint* privat (com crear un esdeveniment), el nostre `api_client` s'ha d'identificar. DRF facilita aquesta tasca amb la funció `force_authenticate`.

```python
@pytest.mark.django_db
def test_crear_event_autenticat(api_client):
    # 1. Creem un usuari real a la base de dades
    usuari = User.objects.create_user(username='admin', password='123')
    
    # 2. Forcem l'autenticació del client (Simula fer login / passar el Token)
    api_client.force_authenticate(user=usuari)
    
    # 3. Fem la petició protegida
    response = api_client.post('/api/v1/events/', {'titol': 'Concert', 'preu': '10.50'})
    assert response.status_code == 201
```

#### 7. Cobertura de codi (*Code Coverage*)
De què serveix fer proves si no sabem quina part del nostre codi estem provant realment? La **cobertura** és una mètrica que ens indica el percentatge de línies de codi del nostre projecte que s'han executat durant les proves. 



Per calcular-la, utilitzarem el connector `pytest-cov`. A la terminal, en lloc d'executar simplement `pytest`, li demanarem que generi un informe per a la carpeta `api`:

```bash
uv run pytest --cov=api --cov-report=html
```

Aquesta comanda executarà tots els tests i crearà una nova carpeta anomenada `htmlcov`. Si obriu el fitxer `htmlcov/index.html` amb el vostre navegador, veureu un informe visual detallat. Us marcarà en verd les línies de codi que estan perfectament provades i en vermell aquelles on els vostres tests encara no hi han arribat. És una eina indispensable per garantir la qualitat a producció!

---

**Referències:**
* [Documentació oficial de pytest](https://docs.pytest.org/en/latest/)
* [Guia de pytest-django](https://pytest-django.readthedocs.io/)
* [Testing a Django REST Framework (Clients API)](https://www.django-rest-framework.org/api-guide/testing/)
* [pytest-cov: Comprovant la cobertura](https://pytest-cov.readthedocs.io/en/latest/)
