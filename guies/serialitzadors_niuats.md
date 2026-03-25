# Serialitzadors Niuats (*Nested Serializers*) a DRF

**Resum:** Aquesta guia explica com rebre i enviar estructures de dades complexes i relacionades (com ara una comanda que conté múltiples entrades) en una sola petició JSON, evitant haver de fer múltiples trucades a la nostra API.

**Índex de continguts:**

1.  Què és un Serialitzador Niuat?
2.  Com s'implementen a Django REST Framework?
3.  Exemple Pràctic.
4.  Referències i enllaços relacionats.

## 1\. Què és un Serialitzador Niuat?

En una API REST bàsica, cada endpoint sol retornar dades d'una sola taula (un llistat d'esdeveniments, per exemple). Però en el món real, les dades estan relacionades. Un **serialitzador niuat** permet incloure l'estructura completa d'un objecte fill directament dins del JSON de l'objecte pare.
En lloc de rebre només un llistat d'IDs d'entrades dins d'una compra, podem rebre (o enviar) tota la informació de les entrades de cop.

## 2\. Com s'implementen a Django REST Framework?

A DRF, per niuar dades només cal utilitzar un serialitzador com si fos un camp dins d'un altre serialitzador. Si la relació és de "molts" (una compra té moltes entrades), utilitzarem l'atribut `many=True`.

## 3\. Exemple Pràctic

Imagina que volem que l'API de Compres accepti directament un llistat de les entrades que l'usuari vol comprar:

```python
from rest_framework import serializers

# 1. Definim el serialitzador "fill"
class EntradaSerializer(serializers.Serializer):
    esdeveniment_id = serializers.IntegerField()
    quantitat = serializers.IntegerField()

# 2. Definim el serialitzador "pare" i hi incrustem el fill
class CompraSerializer(serializers.Serializer):
    usuari_id = serializers.IntegerField()
    # Aquí fem la màgia: una llista d'entrades dins de la compra!
    entrades = EntradaSerializer(many=True) 
```

**JSON resultant:**
Això permet que el *frontend* (Vue) ens enviï un paquet de dades complet en una sola petició HTTP:

```json
{
  "usuari_id": 4,
  "entrades": [
    { "esdeveniment_id": 1, "quantitat": 2 },
    { "esdeveniment_id": 3, "quantitat": 1 }
  ]
}
```

## 4\. Referències i enllaços relacionats

  * 🔗 [Documentació Oficial DRF: Serializers (Nested relationships)](https://www.django-rest-framework.org/api-guide/serializers/%23dealing-with-nested-objects)
  * 🔗 [Documentació Oficial DRF: Writable nested serializers](https://www.django-rest-framework.org/api-guide/serializers/%23writable-nested-serializers)
