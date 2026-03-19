# Introducció a Vue 3 i Composition API

Benvinguts al Frontend! Fins ara hem treballat amb Django, on el servidor s'encarrega de processar les dades. Ara, amb **Vue 3**, passem a una arquitectura d'**Aplicació d'Una Sola Pàgina (SPA)**. Això vol dir que el navegador descarrega l'aplicació web una sola vegada i, a partir d'aquí, només demana les "dades crues" (JSON) al servidor per actualitzar la interfície dinàmicament sense recarregar la pàgina.

Aquesta guia us servirà com a "kit de supervivència" per entendre els conceptes clau de Vue 3 abans de posar-vos a programar.

## 1. El Component d'Un Sol Fitxer (SFC)
A Vue, la interfície es divideix en peces reutilitzables anomenades **components**. Cada component es guarda en un fitxer `.vue` i consta de tres parts ben diferenciades:

```vue
<script setup>
// 1. LÒGICA (JavaScript): Aquí van les variables, funcions i crides a l'API.
// El 'setup' fa que tot el que definim aquí sigui usable a l'HTML automàticament.
</script>

<template>
  <div>Hola Món!</div>
</template>

<style scoped>
/* 3. DISSENY (CSS): L'atribut 'scoped' garanteix que aquests estils 
   només s'apliquin a aquest component i no trenquin la resta de la web. */
div { color: blue; }
</style>
```

## 2. Reactivitat: La màgia de `ref`
A JavaScript tradicional, si canvies una variable, has de buscar l'element HTML manualment i actualitzar-lo. A Vue, utilitzem **variables reactives**. Si el valor de la variable canvia, Vue actualitza l'HTML automàticament.

Per fer una variable reactiva, utilitzem `ref`:

```vue
<script setup>
import { ref } from 'vue';

// Creem una variable reactiva amb valor inicial 0
const comptador = ref(0);

const incrementar = () => {
  comptador.value++; // Important: per accedir al valor d'un ref a JS, usem .value
};
</script>

<template>
  <button @click="incrementar">Has fet clic {{ comptador }} vegades</button>
</template>
```

## 3. Directives Bàsiques
Les directives són atributs especials de Vue (comencen per `v-` o símbols) que donen "superpoders" a l'HTML.

* **`v-if` / `v-else` (Condicionals):** Mostra o amaga elements del DOM segons una condició.
  ```html
  <p v-if="loading">Carregant dades...</p>
  <p v-else>Dades carregades correctament!</p>
  ```
* **`v-for` (Bucles):** Repeteix un element HTML per cada ítem d'una llista. Obliga a usar un `:key` únic.
  ```html
  <ul>
    <li v-for="alumne in alumnes" :key="alumne.id">{{ alumne.nom }}</li>
  </ul>
  ```
* **`@` o `v-on` (Esdeveniments):** Escolta accions de l'usuari (clics, tecles, formularis).
  ```html
  <button @click="guardarDades">Guardar</button>
  ```
* **`:` o `v-bind` (Atributs dinàmics):** Enllaça un atribut HTML a una variable de JavaScript.
  ```html
  <img :src="imatgeUrl" :alt="descripcioImatge">
  ```

## 4. Comunicació entre Components
Quan dividim la nostra web en components (ex: una `Llista` que conté moltes `Targetes`), necessitem que es parlin entre ells.

* **Props (De Pare a Fill):** El pare passa dades al fill de dalt a baix. Són només de lectura.
* **Emits (De Fill a Pare):** El fill avisa el pare que ha passat alguna cosa (ex: "Han fet clic al meu botó d'esborrar").

Entendre aquesta direccionalitat és clau per mantenir l'aplicació ordenada i fàcil de depurar.
