# Validació de Dades als Serialitzadors

**Resum:** Aquesta guia detalla els mecanismes per assegurar que les dades rebudes des del *frontend* són correctes i compleixen les nostres regles de negoci (com per exemple, comprovar que hi ha prou aforament) abans de processar-les i desar-les a la base de dades.

**Índex de continguts:**

1.  Per què necessitem validar?
2.  Mètodes de validació a DRF.
3.  Exemple Pràctic.
4.  Referències i enllaços relacionats.

#### 1\. Per què necessitem validar?

Mai hem de confiar en les dades que ens envia el *frontend*. Abans d'intentar guardar res a la base de dades, hem d'assegurar-nos que les dades són lògiques. Si no ho fem, el sistema podria fallar o podríem acabar venent més entrades de les disponibles físicament.

#### 2\. Mètodes de validació a DRF

DRF ens ofereix dues maneres principals d'afegir regles de validació personalitzades dins dels nostres `serializers`:

  * **Validació de camp (`validate_<nom_del_camp>`):** S'utilitza quan només ens importa revisar un valor aïllat.
  * **Validació a nivell d'objecte (`validate`):** S'utilitza quan necessitem comparar diversos camps alhora, o quan hem de consultar la base de dades abans de donar el vistiplau (com és el cas de comprovar l'aforament).

#### 3\. Exemple Pràctic

Anem a validar que un usuari no demani una quantitat d'entrades superior a l'aforament actual d'un esdeveniment. En cas d'error, aixecarem una excepció `serializers.ValidationError`.

```python
from rest_framework import serializers
from .models import Event

class LiniaCistellaSerializer(serializers.Serializer):
    esdeveniment_id = serializers.IntegerField()
    quantitat = serializers.IntegerField()

    def validate(self, data):
        esdeveniment_id = data['esdeveniment_id']
        quantitat_demanada = data['quantitat']

        try:
            esdeveniment = Event.objects.get(id=esdeveniment_id)
        except Event.DoesNotExist:
            raise serializers.ValidationError("L'esdeveniment no existeix.")

        # Apliquem la nostra regla de negoci
        if quantitat_demanada > esdeveniment.capacitat:
            # Això aturarà l'execució i retornarà un error HTTP 400
            raise serializers.ValidationError(
                f"Error: Només queden {esdeveniment.capacitat} places lliures."
            )
        
        return data
```

#### 4\. Referències i enllaços relacionats

  * 🔗 [Documentació Oficial DRF: Validation](https://www.django-rest-framework.org/api-guide/serializers/%23validation)
  * 🔗 [Documentació Oficial DRF: Object-level validation](https://www.django-rest-framework.org/api-guide/serializers/%23object-level-validation)
