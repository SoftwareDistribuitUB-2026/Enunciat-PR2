# Sessió 3: Navegació (Vue Router) i Estat Global (Cistella amb Pinia)

En aquesta sessió convertirem el nostre component aïllat en una aplicació web completa. Afegirem diferents "pàgines" (Vistes) utilitzant **Vue Router** i construirem una cistella de la compra persistent utilitzant **Pinia** i el `LocalStorage` del navegador.

**Objectius de la sessió:**
1. Configurar `vue-router` per crear una barra de navegació i diverses rutes (Home, Admin, Cistella, Compres).
2. Entendre la composició de components creant un `ModifiableEventItem` per a la vista d'administració.
3. Configurar **Pinia** per gestionar l'estat global de l'aplicació.
4. Crear la funcionalitat d'afegir, modificar i esborrar elements de la cistella, guardant-ho al `LocalStorage`.

**Guies relacionades:**
Abans o durant la realització d'aquesta sessió, us recomanem consultar:
* 📖 **[Gestió d'Estat amb Pinia](../guies/estat_pinia.md):** Guia essencial per entendre com funciona l'estat global compartit entre múltiples components.
* 📖 **[Documentació de Vue Router](https://router.vuejs.org/):** Per aprofundir en rutes dinàmiques i protecció de rutes.

---

## 1. Configuració de Vue Router i el Menú de Navegació

Quan vam crear el projecte amb Vite, probablement ja es va instal·lar Vue Router. Si no és així, executeu `npm install vue-router`.

### 1.1. Definir les Vistes (Views)
Creeu una carpeta `src/views/` (si no existeix) i afegiu-hi els següents fitxers (poden estar buits amb un simple `<h1>` per ara):
* `HomeView.vue` (Aquí mourem la llista d'esdeveniments de la Sessió 2)
* `AdminView.vue` (Per gestionar esdeveniments)
* `CartView.vue` (La cistella)
* `OrdersView.vue` (L'historial de compres)

### 1.2. Configurar el Router (`src/router/index.js`)
Creeu o modifiqueu el fitxer d'enrutament per connectar les URLs amb els components visuals.

```javascript
import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import AdminView from '../views/AdminView.vue'
import CartView from '../views/CartView.vue'
import OrdersView from '../views/OrdersView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/admin', name: 'admin', component: AdminView },
    { path: '/cart', name: 'cart', component: CartView },
    { path: '/orders', name: 'orders', component: OrdersView }
  ]
})

export default router
```

### 1.3. La Barra de Navegació a `App.vue`
Substituïu el contingut de `App.vue` per incloure els enllaços (`<router-link>`) i el contenidor on es carregaran les pàgines (`<router-view>`).

```vue
<template>
  <header>
    <nav class="navbar">
      <div class="logo">🎟️ TicketFlow</div>
      <div class="links">
        <router-link to="/">Inici</router-link>
        <router-link to="/admin">Administració</router-link>
        <router-link to="/cart">Cistella</router-link>
        <router-link to="/orders">Les meves compres</router-link>
      </div>
    </nav>
  </header>

  <main>
    <router-view />
  </main>
</template>

<style scoped>
.navbar { display: flex; justify-content: space-between; padding: 1rem; background: #333; color: white; }
.links a { color: white; text-decoration: none; margin-left: 1rem; }
.links a.router-link-active { font-weight: bold; text-decoration: underline; }
</style>
```
*Assegureu-vos de moure el codi de la Sessió 2 (el llistat) dins de `HomeView.vue`.*

---

## 2. Composició per a l'Admin: `ModifiableEventItem`

A la vista d'Administració (`AdminView.vue`) volem mostrar els mateixos esdeveniments, però amb botons per Editar i Eliminar. 

A Vue no utilitzem l'herència clàssica orientada a objectes. Utilitzem la **composició (Wrapper Components)**. Crearem un component que importi el `EventItem` normal i li afegeixi els controls addicionals.

Creeu `src/components/ModifiableEventItem.vue`:

```vue
<script setup>
import EventItem from './EventItem.vue';

const props = defineProps({
    event: { type: Object, required: true }
});

const handleDelete = async () => {
    if (confirm(`Segur que vols eliminar ${props.event.name}?`)) {
        console.log(`Cridant al servei per eliminar l'event amb ID: ${props.event.id}`);
        // TODO: Cridar a api.delete(`/events/${props.event.id}/`) (Treball fora del laboratori)
    }
};

const handleEdit = () => {
    console.log(`Obrint formulari d'edició per l'event amb ID: ${props.event.id}`);
    // TODO: Implementar la lògica d'edició (Treball fora del laboratori)
};
</script>

<template>
  <div class="admin-card">
    <EventItem :event="event" />
    
    <div class="admin-actions">
      <button @click="handleEdit" class="btn-edit">✏️ Editar</button>
      <button @click="handleDelete" class="btn-delete">🗑️ Eliminar</button>
    </div>
  </div>
</template>

<style scoped>
.admin-card { border: 2px dashed #f39c12; margin-bottom: 1rem; }
.admin-actions { display: flex; gap: 0.5rem; padding: 0.5rem; background: #fff8e1; }
</style>
```
*Feu que `AdminView.vue` demani la llista d'esdeveniments a l'API i els renderitzi utilitzant aquest nou `ModifiableEventItem`.*

---

## 3. L'Estat Global: La Cistella amb Pinia i LocalStorage

Si afegim un element a la cistella des de la `HomeView` i naveguem a la `CartView`, les dades s'esborren si només utilitzem `ref` locals. Necessitem **Pinia**.



### 3.1. Configurar el Store de la Cistella (`src/stores/cart.js`)
Si no teniu Pinia instal·lat: `npm install pinia`. (*Recordeu registrar-lo a `main.js` amb `app.use(createPinia())`*).

Creeu el fitxer `src/stores/cart.js`. Utilitzarem la Composition API de Pinia i afegirem persistència amb `localStorage` perquè la cistella sobrevisqui si tanquem la pestanya.

```javascript
import { defineStore } from 'pinia';
import { ref, watch } from 'vue';

export const useCartStore = defineStore('cart', () => {
  // 1. ESTAT: Llegim del LocalStorage al carregar, o iniciem buit
  const items = ref(JSON.parse(localStorage.getItem('ticketflow-cart')) || []);

  // Guardar automàticament al LocalStorage cada cop que 'items' canviï
  watch(items, (newItems) => {
    localStorage.setItem('ticketflow-cart', JSON.stringify(newItems));
  }, { deep: true });

  // 2. ACCIONS
  const addToCart = (event) => {
    const existingItem = items.value.find(item => item.id === event.id);
    if (existingItem) {
      existingItem.quantity++;
    } else {
      items.value.push({ ...event, quantity: 1 });
    }
  };

  const removeFromCart = (eventId) => {
    items.value = items.value.filter(item => item.id !== eventId);
  };

  const updateQuantity = (eventId, quantity) => {
    const item = items.value.find(item => item.id === eventId);
    if (item && quantity > 0) {
      item.quantity = quantity;
    } else if (quantity === 0) {
      removeFromCart(eventId);
    }
  };

  return { items, addToCart, removeFromCart, updateQuantity };
});
```

### 3.2. Afegir a la cistella des de `EventItem.vue`
Ara connectem el nostre component visual amb el Store. Modifiqueu `EventItem.vue` per incloure el botó:

```vue
<script setup>
import { useCartStore } from '../stores/cart'; // Importem el store

defineProps({ event: { type: Object, required: true } });

const cartStore = useCartStore(); // Instanciem el store
</script>

<template>
  <div class="event-card">
    <h3>{{ event.name }}</h3>
    <button @click="cartStore.addToCart(event)">🛒 Afegir a la Cistella</button>
  </div>
</template>
```

### 3.3. Visualitzar i Modificar la Cistella (`CartView.vue`)
Finalment, mostrem els elements a la pàgina de la cistella, permetent modificar-ne les quantitats.

```vue
<script setup>
import { useCartStore } from '../stores/cart';

const cartStore = useCartStore();
</script>

<template>
  <div>
    <h2>La meva Cistella</h2>
    
    <div v-if="cartStore.items.length === 0">
      <p>La cistella està buida.</p>
    </div>
    
    <div v-else>
      <div v-for="item in cartStore.items" :key="item.id" class="cart-item">
        <h4>{{ item.name }}</h4>
        <p>Preu unitari: {{ item.price }} €</p>
        
        <div class="controls">
          <button @click="cartStore.updateQuantity(item.id, item.quantity - 1)">-</button>
          <span> {{ item.quantity }} </span>
          <button @click="cartStore.updateQuantity(item.id, item.quantity + 1)">+</button>
          
          <button @click="cartStore.removeFromCart(item.id)" class="btn-delete">🗑️ Eliminar</button>
        </div>
      </div>
      
      <button class="btn-checkout">Procedir al Pagament</button>
    </div>
  </div>
</template>

<style scoped>
.cart-item { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #ddd; padding: 1rem 0; }
.controls { display: flex; gap: 0.5rem; align-items: center; }
.btn-delete { color: red; }
</style>
```

---

## 🏠 Treball fora del laboratori

Ara que ja teniu tota la "fontaneria" del frontend (Navegació i Estat local) funcionant de meravella, és el moment de connectar aquestes accions simulades amb l'API real del backend:

1. **Implementar l'Eliminació i Edició (Admin):**
   * Aneu a `ModifiableEventItem.vue` i canvieu els `console.log()` per crides reals al backend utilitzant la vostra instància d'Axios (`api.delete(...)` i `api.put(...)` o `api.patch(...)`).
   * *Repte:* Quan s'esborri un element amb èxit a l'API, heu d'emetre un esdeveniment al pare (`AdminView`) perquè l'esborri també de l'array visual, o tornar a demanar la llista sencera per actualitzar la pantalla.

2. **Implementar el Checkout de la Cistella:**
   * A la vista `CartView.vue`, el botó "Procedir al Pagament" ha d'agafar tots els elements de `cartStore.items`.
   * Ha de fer una petició `POST` a l'endpoint corresponent del vostre Django (ex: `/api/v1/orders/` o `/api/v1/tickets/`) passant el detall de la compra.
   * Si la compra és exitosa (Status 201), heu de buidar la cistella (`cartStore.items = []`) i redirigir l'usuari a la vista `OrdersView` usant `router.push('/orders')`.
```
