# Sessió 5: Finalització de Compres amb Transaccions i Pla de Testing Backend

En aquesta sessió implementarem el tancament de la compra de manera segura al backend. La idea clau és que una compra amb múltiples línies s'ha de confirmar **tota sencera o no confirmar-se**. Si algun element no disposa d'estoc suficient, el sistema ha de desfer tota l'operació automàticament (*rollback*).

**Objectius de la sessió:**

1. Implementar un endpoint de finalització de compra (checkout) al backend.
2. Introduir el concepte de transacció atòmica (`transaction.atomic`) a la vista de DRF.
3. Garantir consistència d'estoc: no permetre compres parcials quan una línia falla.
4. Controlar errors funcionals (estoc insuficient, quantitats invàlides, etc.) amb respostes HTTP coherents.
5. Definir i implementar tests de backend per validar permisos, accés i comportament funcional del checkout.

**Guies relacionades:**

* 📖 [Gestió d'errors i operacions atòmiques](../guies/drf_gestio_errors.md)
* 📖 [Configuració i utilització de pytest amb Django i DRF](../guies/pytest_django_drf.md)
* 📖 [Aplicant la Seguretat al Backend](../guies/seguretat_backend_django.md)
* 📖 [Creant APIs amb Django REST Framework](../guies/drf_rest_apis.md)

---

## 1. Context funcional: què vol dir "finalitzar compra"?

Fins ara, la cistella s'ha tractat sobretot des del frontend. Ara necessitem un pas final al backend que faci la compra real:

1. Rebre totes les línies de compra en una única petició.
2. Comprovar disponibilitat per a cada esdeveniment.
3. Registrar les entrades només si **totes** les línies són vàlides.
4. Crear el registre de compra i el detall de línies.
5. Retornar resposta d'èxit amb resum de la compra.

Si una línia no compleix condicions (per exemple, estoc insuficient), no s'ha de descomptar res ni crear una compra "a mitges".

---

## 2. Disseny de l'endpoint de checkout

Per resoldre aquesta funcionalitat, treballarem amb un endpoint específic:

* **Mètode:** `POST`
* **Ruta:** `/api/v1/checkout/`
* **Permís:** Usuari autenticat

Durant aquesta sessió utilitzarem aquestes rutes:

* **Llistat/detall de compres:** `/api/v1/compres/`
* **Finalització de compra:** `/api/v1/checkout/`

### Exemple de payload d'entrada

```json
{
    "usuari_id": 5,
    "entrades": [
        {"esdeveniment_id": 3, "quantitat": 2},
        {"esdeveniment_id": 7, "quantitat": 1}
  ]
}
```

### Exemple de resposta correcta

```json
{
  "id": 42,
  "usuari": 5,
  "total": "65.00",
    "entrades": [
        {"esdeveniment_id": 3, "quantitat": 2, "preu_unitari": "20.00"},
        {"esdeveniment_id": 7, "quantitat": 1, "preu_unitari": "25.00"}
  ]
}
```

### Exemple de resposta d'error (sense rollback parcial)

```json
{
  "detail": "No hi ha prou places per a l'esdeveniment 7"
}
```

---

## 3. Implementació pas a pas al backend

> Nota: adapteu els noms de models/camps als que ja tingueu al vostre projecte (`Compra`, `Entrada`, `Event`, etc.).

### 3.1. Definir un serializer d'entrada per validar dades

Creeu un serializer específic per al checkout (a `serializers.py`) per validar l'estructura d'entrada i les quantitats:

```python
from rest_framework import serializers


class CheckoutItemSerializer(serializers.Serializer):
    esdeveniment_id = serializers.IntegerField(min_value=1)
    quantitat = serializers.IntegerField(min_value=1)


class CheckoutSerializer(serializers.Serializer):
    usuari_id = serializers.IntegerField(min_value=1)
    entrades = CheckoutItemSerializer(many=True)

    def validate_entrades(self, value):
        if not value:
            raise serializers.ValidationError("La compra ha de contenir almenys una entrada")
        return value
```

### 3.2. Implementar la vista amb `transaction.atomic`

A `views.py`, implementeu una vista específica de checkout (separada del `ViewSet` de compres). El punt crític és executar tota la lògica dins una transacció:

```python
from django.db import transaction
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Event, Compra, Entrada
from .serializers import CheckoutSerializer, CompraSerializer


class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        entrades = serializer.validated_data['entrades']

        compra = Compra.objects.create(usuari=request.user)

        for item in entrades:
            event = Event.objects.select_for_update().get(pk=item['esdeveniment_id'])
            qty = item['quantitat']

            if event.capacitat < qty:
                raise ValidationError(
                    {"detail": f"No hi ha prou places per a l'esdeveniment {event.id}"}
                )

            # La capacitat és una propietat calculada: no s'actualitza directament.
            # L'estoc disponible varia en crear les entrades associades a la compra.
            Entrada.objects.create(
                compra=compra,
                esdeveniment=event,
                quantitat=qty,
                preu_unitari=event.preu,
            )

        output = CompraSerializer(compra)
        return Response(output.data, status=status.HTTP_201_CREATED)
```

A `urls.py`, registreu-la explícitament:

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CompraViewSet, CheckoutView

router = DefaultRouter()
router.register(r'compres', CompraViewSet, basename='compres')

urlpatterns = [
    path('api/v1/', include(router.urls)),
    path('api/v1/checkout/', CheckoutView.as_view(), name='checkout'),
]
```

### 3.3. Per què això evita compres parcials?

Perquè `transaction.atomic()` garanteix propietat de "tot o res":

1. Si cap error apareix, es confirma tot (`COMMIT`).
2. Si apareix una excepció (ex: `ValidationError` per estoc insuficient), Django marca `ROLLBACK`.
3. El rollback desfà tant la creació de `Compra` i `Entrada` com qualsevol altre efecte aplicat dins la transacció.

### 3.4. Afegir el control de permisos i d'accés a les consultes

A més del checkout, assegureu que un usuari normal només pugui veure les seves compres:

```python
def get_queryset(self):
    if self.request.user.is_staff:
        return Compra.objects.all()
    return Compra.objects.filter(usuari=self.request.user)
```

Això és necessari per cobrir correctament les proves d'accés i autoria.

---

## 4. Proves manuals mínimes (curl)

Amb backend en marxa i usuari autenticat:

```bash
curl -X POST http://localhost:8000/api/v1/checkout/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
        "usuari_id": 1,
        "entrades": [
            {"esdeveniment_id": 1, "quantitat": 2},
            {"esdeveniment_id": 2, "quantitat": 1}
    ]
  }'
```

Comproveu després l'estoc de cada `Event` i que s'ha creat exactament una compra amb les seves línies.

---

## PART 5: Tasques fora del laboratori (Treball Autònom)

En aquest bloc de treball autònom fareu dues línies de feina complementàries:

1. Consolidar el backend del checkout amb una bateria de proves.
2. Completar el frontend amb la vista de registre d'usuaris.

L'objectiu és assegurar, alhora, la robustesa del procés de compra i una experiència d'accés completa a l'aplicació.

### 5.1. Exemple de test backend 1: compra correcta

```python
import pytest
from rest_framework import status

from api.models import Compra


@pytest.mark.django_db
def test_checkout_ok_authenticated_user(api_client, user_factory, event_factory):
    user = user_factory()
    event_a = event_factory(capacitat=10, preu='20.00')
    event_b = event_factory(capacitat=5, preu='15.00')

    api_client.force_authenticate(user=user)

    payload = {
        "usuari_id": user.id,
        "entrades": [
            {"esdeveniment_id": event_a.id, "quantitat": 2},
            {"esdeveniment_id": event_b.id, "quantitat": 1},
        ]
    }

    response = api_client.post('/api/v1/checkout/', payload, format='json')

    assert response.status_code == status.HTTP_201_CREATED
    event_a.refresh_from_db()
    event_b.refresh_from_db()
    assert event_a.capacitat == 8  # propietat calculada després de crear entrades
    assert event_b.capacitat == 4
    assert Compra.objects.filter(usuari=user).count() == 1
```

### 5.2. Exemple de test backend 2: fallada parcial amb rollback total

```python
import pytest
from rest_framework import status

from api.models import Compra


@pytest.mark.django_db
def test_checkout_partial_unavailability_rolls_back_all(api_client, user_factory, event_factory):
    user = user_factory()
    ok_event = event_factory(capacitat=10, preu='20.00')
    failing_event = event_factory(capacitat=1, preu='50.00')

    api_client.force_authenticate(user=user)

    payload = {
        "usuari_id": user.id,
        "entrades": [
            {"esdeveniment_id": ok_event.id, "quantitat": 2},
            {"esdeveniment_id": failing_event.id, "quantitat": 3}
        ]
    }

    response = api_client.post('/api/v1/checkout/', payload, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    ok_event.refresh_from_db()
    failing_event.refresh_from_db()

    # Rollback total: no es toca cap estoc i no es crea compra
    assert ok_event.capacitat == 10
    assert failing_event.capacitat == 1
    assert Compra.objects.filter(usuari=user).count() == 0
```

### 5.3. Casos de prova obligatoris (backend)

| ID | Què cal provar | Dades d'entrada | Resultat esperat |
| :-- | :-- | :-- | :-- |
| T01 | Usuari no autenticat intenta checkout | `POST /checkout` sense token | `403 Forbidden` |
| T02 | Usuari autenticat fa compra vàlida d'1 línia | Estoc suficient | `201 Created`, compra creada i disponibilitat actualitzada |
| T03 | Usuari autenticat fa compra vàlida de múltiples línies | Totes les línies amb estoc suficient | `201 Created`, compra creada amb total correcte i disponibilitat actualitzada |
| T04 | Quantitat invàlida (0 o negativa) | `quantitat <= 0` | `400 Bad Request` de validació |
| T05 | Payload buit | `entrades: []` | `400 Bad Request` amb missatge de validació |
| T06 | Event inexistent | `esdeveniment_id` no existent | `400` o `404` segons implementació, sense canvis a BD |
| T07 | Fallada total per manca d'estoc a totes les línies | Totes les línies excedeixen estoc | `400`, no es crea compra, disponibilitat intacta |
| T08 | Fallada parcial (una línia falla, altres correctes) | 1 línia sense estoc + 1 línia correcta | `400`, **rollback total**, cap compra creada |
| T09 | Control d'accés a detall de compra d'un altre usuari | `GET /compres/{id}` d'altri | `404` (si filtreu queryset) o `403` (si useu permís object-level) |
| T10 | Usuari només veu les seves compres | `GET /compres/` amb compres de diversos usuaris | Resposta filtrada només a compres pròpies |
| T11 | Usuari admin llista compres globals | `GET /compres/` amb admin | Veu totes les compres |
| T12 | Integritat del total | Compra amb preus coneguts | `total` retornat coincideix amb suma de línies |

### 5.4. Tasques a realitzar

1. **Implementar els tests del checkout al backend:**
    * Utilitzeu els exemples 5.1 i 5.2 com a punt de partida.
    * Cobriu, com a mínim, els casos de la taula 5.3 (permisos, accés, compres correctes i compres fallides totals/parcials).

2. **Afegir registre d'usuaris al frontend (`RegisterView.vue`):**
    * Creeu una vista de registre que faci una crida `POST` (sense token) a l'endpoint de creació d'usuaris.
    * El formulari ha d'incloure, com a mínim, `username`, `email`, `password`, `confirm_password` i un `checkbox` obligatori d'acceptació de condicions.
    * Si `password` i `confirm_password` no coincideixen, no s'ha d'enviar el formulari i s'ha de mostrar un missatge d'error clar.
    * Si el `checkbox` d'acceptació no està marcat, no s'ha d'enviar el formulari i s'ha de mostrar un missatge d'error clar.

3. **Verificació final i lliurament:**
    * Comproveu que l'endpoint `POST /api/v1/checkout/` funciona correctament i respecta el comportament transaccional (rollback total quan calgui).
    * Executeu la bateria de proves del backend i verifiqueu que passen els casos clau del checkout.
    * Prepareu la PR setmanal amb un resum de proves executades i resultats.