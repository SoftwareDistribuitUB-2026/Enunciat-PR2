# Gestió d'Errors i Transaccions Atòmiques

**Resum:** Com evitar inconsistències a la base de dades aplicant la regla del "Tot o Res" en operacions complexes (com un procés de *Checkout*). Aprendrem a utilitzar transaccions atòmiques a Django i entendre com DRF gestiona els errors HTTP.

**Índex de continguts:**

1.  Com gestiona els errors DRF?
2.  El problema de les compres a mitges.
3.  La solució: Transaccions Atòmiques.
4.  Exemple Pràctic.
5.  Referències i enllaços relacionats.

## 1\. Com gestiona els errors DRF?

Quan aixequeu un error amb `raise serializers.ValidationError(...)`, Django REST Framework l'intercepta automàticament abans que l'aplicació falli. DRF construeix una resposta HTTP neta amb un codi d'estat **400 Bad Request** i envia el text de l'error en format JSON perquè el *frontend* ho mostri a l'usuari.

## 2\. El problema de les compres a mitges

Imagineu un *Checkout* on un usuari compra entrades per a dos esdeveniments diferents:

1.  Es crea la compra general (OK).
2.  Es guarden les entrades del 1r esdeveniment (OK).
3.  Es validen les entrades del 2n esdeveniment i no hi ha lloc (ERROR\!).

Si el procés s'atura aquí, la base de dades es quedarà en un estat inconsistent: l'usuari haurà fet una compra incompleta.

## 3\. La solució: Transaccions Atòmiques

Hem de poder dir-li a la base de dades: *"Si falla qualsevol pas, desfés-ho tot com si no hagués passat mai"*.
Una transacció **atòmica** aplica la regla del "Tot o Res". A Django, s'aconsegueix embolicant la nostra lògica amb el decorador `@transaction.atomic`. Si dins del bloc de codi hi ha qualsevol excepció, Django farà un **Rollback** de la base de dades, esborrant qualsevol registre que s'hagi creat dins d'aquell bloc.

## 4\. Exemple Pràctic

```python
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class CheckoutView(APIView):
    
    @transaction.atomic # Marquem tota la funció com a atòmica
    def post(self, request):
        try:
            # 1. Creem una compra (si després falla, s'esborrarà sola)
            nova_compra = Compra.objects.create(usuari=request.user)

            # 2. Processar línies
            for linia in request.data['entrades']:
                # ... (comprovar aforament) ...
                
                if sense_aforament:
                    # AIXÒ ÉS LA CLAU: Llençar una excepció cancel·la la transacció
                    raise ValueError("No hi ha prou lloc.")
                
                Entrada.objects.create(compra=nova_compra, ...)

            return Response({"missatge": "Compra realitzada!"}, status=status.HTTP_201_CREATED)

        except ValueError as e:
            # La BD ja ha desfet els canvis. Informem a l'usuari.
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
```

## 5\. Referències i enllaços relacionats

  * 🔗 [Documentació Oficial Django: Database Transactions (atomic)](https://docs.djangoproject.com/en/stable/topics/db/transactions/%23django.db.transaction.atomic)
  * 🔗 [Documentació Oficial DRF: Exceptions](https://www.django-rest-framework.org/api-guide/exceptions/)
