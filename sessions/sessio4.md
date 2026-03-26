# Sessió 4: Autenticació JWT i Control d'Accés (Backend i Frontend)

Fins ara hem construït una aplicació oberta, però en el món real necessitem saber qui està utilitzant el nostre sistema per permetre-li fer certes accions o denegar-n'hi d'altres. En aquesta sessió donarem identitat als nostres usuaris mitjançant **JSON Web Tokens (JWT)**. Connectarem el nostre backend perquè emeti i validi aquests *tokens*, i prepararem el frontend per gestionar l'inici de sessió de forma segura.

**Objectius de la sessió:**

1.  Comprendre i aplicar el flux d'autenticació mitjançant JSON Web Tokens (JWT).
2.  Configurar el backend per emetre tokens i protegir els endpoints mitjançant regles d'autorització globals i específiques.
3.  Crear rutes personalitzades al backend per facilitar la recuperació de la sessió (`/users/me/`).
4.  Gestionar l'estat global de la sessió de l'usuari al frontend utilitzant l'emmagatzematge local.
5.  Configurar el client HTTP per adjuntar automàticament les credencials a totes les peticions segures.
6.  Protegir la navegació del frontend restringint l'accés a vistes privades.
7.  Implementar un mecanisme de renovació automàtica de credencials (Refresh Token) de forma transparent per a l'usuari.

**Guies relacionades:**
Abans o durant la realització d'aquesta sessió, us recomanem consultar:

  * 📖 **[Conceptes de Seguretat Web](../guies/seguretat_conceptes.md):** Per entendre l'estàndard JWT i la diferència vital entre Autenticació i Autorització.
  * 📖 **[Aplicant la Seguretat al Backend](../guies/seguretat_backend_django.md):** Per veure com Django emet tokens JWT i com crear permisos personalitzats.
  * 📖 **[Autenticació i Dades Sensibles al Frontend](../guies/seguretat_frontend_vue.md):** Sobre com desar el token al `localStorage` i interceptar peticions HTTP.
  * 📖 **[Entenent CORS i CSRF](../guies/seguretat_cors_csrf.md):** Per entendre com el JWT ens protegeix per defecte contra atacs de falsificació de peticions.

-----

## PART 1: Backend - Gestionant Tokens i Protegint Usuaris

### 1.1. Instal·lació i configuració de SimpleJWT

El primer pas és ensenyar al nostre backend a generar i validar tokens JWT.
Obriu el terminal al vostre entorn de backend i afegiu la llibreria com a dependència utilitzant `uv`:

```bash
uv add djangorestframework-simplejwt
```

A continuació, obriu el fitxer `settings.py` del vostre projecte Django i feu dues modificacions clau.

Primer, afegiu la nova llibreria a les aplicacions instal·lades perquè Django la reconegui en arrencar:

```python
# settings.py
INSTALLED_APPS = [
    # ... les aplicacions per defecte de Django ...
    'rest_framework',
    'rest_framework_simplejwt', # <-- Afegim aquesta línia
    # ... les teves aplicacions ...
]
```

Segon, al mateix fitxer, indiqueu a Django REST Framework que utilitzi JWT com a mètode d'autenticació i que, per defecte, totes les rutes requereixin estar identificat:

```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}
```

### 1.2. Els endpoints d'Autenticació i proves

Ara afegirem els endpoints (URLs) per demanar tokens. Obriu l'arxiu `urls.py` principal de l'API i afegiu les rutes de SimpleJWT:

```python
# urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # ... les vostres altres rutes ...
    
    # Endpoints per a l'autenticació JWT
    path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
```

**Provem-ho\!**
Assegureu-vos que teniu un superusuari creat a Django i engegueu el servidor utilitzant `uv run` per garantir que s'executa dins l'entorn virtual correcte:

```bash
uv run python manage.py runserver
```

Obriu un terminal nou i feu una petició POST amb `curl` (substituïu les credencials per les vostres):

```bash
curl -X POST http://localhost:8000/api/v1/token/ \
     -H "Content-Type: application/json" \
     -d '{"username": "EL_TEU_USUARI", "password": "LA_TEVA_CONTRASENYA"}'
```

*Si tot ha anat bé, veureu que el servidor us retorna un JSON amb un `access` token llarg i un `refresh` token.*

### 1.3. L'endpoint d'Usuaris i Autorització Personalitzada

Anem a protegir el model d'Usuari. Volem que qualsevol es pugui registrar, però que només tu puguis veure o editar el teu propi perfil.

Creeu un fitxer anomenat `permissions.py` a la vostra aplicació (al costat de `views.py`):

```python
# permissions.py
from rest_framework import permissions

class IsSelfOrAdmin(permissions.BasePermission):
    """
    Permet l'accés complet només als administradors o a l'usuari mateix.
    """
    def has_object_permission(self, request, view, obj):
        # Els administradors sempre poden
        if request.user.is_staff:
            return True
        # L'usuari només pot accedir al seu propi registre
        return obj == request.user
```

Ara, obriu el vostre `views.py`. Com que esteu utilitzant un `ModelViewSet` per als usuaris, definirem quins permisos s'apliquen a cada acció dinàmicament sobreescrivint el mètode `get_permissions()`:

```python
# views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from .serializers import UserSerializer
from .permissions import IsSelfOrAdmin

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        # Si algú vol crear un usuari (registrar-se), deixem passar a tothom
        if self.action == 'create':
            return [AllowAny()]
        
        # Per a la resta d'accions (veure detall, editar, esborrar...), 
        # exigim estar logat i complir la nostra regla personalitzada
        return [IsAuthenticated(), IsSelfOrAdmin()]
```

### 1.4. Comprovem l'Abans i el Després amb `curl`

Anem a veure què hem aconseguit amb aquesta capa de seguretat. Si intentem demanar les dades de l'usuari ID 1 **sense estar logats**, el servidor ens tancarà la porta:

```bash
# Crida SENSE token
curl -X GET http://localhost:8000/api/v1/users/1/

# Resposta del servidor (401 Unauthorized):
# {"detail": "Authentication credentials were not provided."}
```

Per poder entrar, hem d'adjuntar el nostre "passaport" (el JWT) a la capçalera de la petició utilitzant `Authorization: Bearer <token>`:

```bash
# Crida AMB token
curl -X GET http://localhost:8000/api/v1/users/1/ \
     -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Resposta del servidor (200 OK):
# {"id": 1, "username": "joan_test", "email": "joan@example.com"}
```

### 1.5. L'endpoint especial `/users/me/`

Al frontend, quan l'usuari fa login, rep un Token, però **no sap quin és el seu ID d'usuari**. Com pot demanar les seves pròpies dades si no sap el seu número?

La solució estàndard a les APIs REST és crear un endpoint `/me/`. Com que el token ja porta implícit qui ets, el servidor ho sap traduir automàticament.

Afegirem una acció personalitzada al nostre `UserViewSet` utilitzant el decorador `@action`. Torneu a l'arxiu `views.py` i afegiu aquest codi dins de la classe:

```python
# views.py (afegiu aquestes importacions a dalt de tot)
from rest_framework.decorators import action
from rest_framework.response import Response

class UserViewSet(viewsets.ModelViewSet):
    # ... codi anterior (queryset, serializer_class, get_permissions) ...

    # Afegim la ruta /users/me/
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """
        Retorna les dades de l'usuari actualment autenticat a través del token.
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
```

Ara, si fem una petició GET a `http://localhost:8000/api/v1/users/me/` adjuntant el token a la capçalera, el servidor ens retornarà les nostres pròpies dades directament\!

### 1.6. Adaptació dels Tests del Backend

A causa d'aquests canvis, els vostres tests automatitzats fallaran amb un error 401. Heu d'actualitzar els tests de DRF (`APITestCase`) perquè s'autentiquin abans de demanar dades:

```python
# tests.py
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User

class UserApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')

    def test_veure_perfil_amb_autenticacio(self):
        # 1. Autentiquem el client de proves
        self.client.force_authenticate(user=self.user)
        # 2. Fem la petició (podem provar el nou endpoint /me/!)
        response = self.client.get('/api/v1/users/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')

    def test_veure_perfil_sense_autenticacio_falla(self):
        # 1. NO ens autentiquem
        response = self.client.get(f'/api/v1/users/{self.user.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
```

-----

## PART 2: Frontend - La Sessió, Interceptors i Rutes

### 2.1. L'Estat de l'Usuari (Pinia `auth.js`)

Creeu el fitxer `src/stores/auth.js` per gestionar les credencials i desar el token al navegador:

```javascript
import { defineStore } from 'pinia';
import { ref } from 'vue';
import api from '../services/api';

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('access_token') || null);
  const refreshToken = ref(localStorage.getItem('refresh_token') || null);
  const user = ref(null);

  const login = async (username, password) => {
    try {
      const response = await api.post('token/', { username, password });
      
      // Guardem els tokens
      token.value = response.data.access;
      refreshToken.value = response.data.refresh;
      localStorage.setItem('access_token', token.value);
      localStorage.setItem('refresh_token', refreshToken.value);
      
      // Ara podem aprofitar l'endpoint /me/ que hem creat per recuperar l'usuari sencer!
      // Com que l'interceptor (que crearem al punt 2.3) injectarà el token, això funcionarà:
      const userResponse = await api.get('users/me/');
      user.value = userResponse.data; 
      
      return true;
    } catch (error) {
      console.error("Error al login", error);
      return false;
    }
  };

  const logout = () => {
    token.value = null;
    refreshToken.value = null;
    user.value = null;
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  };

  return { token, refreshToken, user, login, logout };
});
```

*(Nota: Fins que no configurem l'Interceptor al Pas 2.3, la crida a `users/me/` dins del login podria fallar. Seguiu llegint\!)*

### 2.2. La vista de Login (`LoginView.vue`) i `App.vue`

Creeu el fitxer `src/views/LoginView.vue`:

```vue
<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const username = ref('');
const password = ref('');
const authStore = useAuthStore();
const router = useRouter();

const handleLogin = async () => {
  const success = await authStore.login(username.value, password.value);
  if (success) {
    router.push('/profile');
  } else {
    alert("Credencials incorrectes");
  }
};
</script>

<template>
  <div class="login-box">
    <h2>Iniciar Sessió</h2>
    <form @submit.prevent="handleLogin">
      <input v-model="username" type="text" placeholder="Usuari" required />
      <input v-model="password" type="password" placeholder="Contrasenya" required />
      <button type="submit">Entrar</button>
    </form>
  </div>
</template>
```

*(Recordeu afegir aquesta vista al vostre `router/index.js` amb la ruta `/login`).*

A `App.vue`, actualitzeu la barra de navegació per incloure el nom de l'usuari:

```vue
<script setup>
import { useAuthStore } from './stores/auth';
const authStore = useAuthStore();
</script>

<template>
<RouterLink v-if="!authStore.token" to="/login" class="nav-link">
    Login
  </RouterLink>

  <RouterLink v-if="authStore.token" to="/profile" class="nav-link">
    <span class="material-symbols-outlined">account_circle</span>
    {{ authStore.user?.username || 'Perfil' }}
  </RouterLink>

  <button v-if="authStore.token" @click="authStore.logout()" class="nav-link logout-btn">
    Sortir
  </button>
</template>
```

### 2.3. Interceptors d'Axios: Injectant el Token

Per no haver d'escriure la capçalera a cada petició (com hem fet manualment amb `curl`), configurarem Axios perquè ho faci per nosaltres. Modifiqueu `src/services/api.js`:

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1/',
  headers: {
    'Content-Type': 'application/json',
  }
});

// Interceptor de REQUEST
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default api;
```

### 2.4. Protecció de rutes (Vue Router Guards)

A `src/router/index.js`, afegiu una metadada `requiresAuth` a les rutes privades i utilitzeu `beforeEach` per protegir-les:

```javascript
// ... importacions ...

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // ...
    { 
      path: '/profile', 
      name: 'profile', 
      component: ProfileView,
      meta: { requiresAuth: true } // Marquem la ruta com a privada
    },
    // ...
  ]
});

// Navigation Guard Global
router.beforeEach((to, from, next) => {
  const isAuthenticated = !!localStorage.getItem('access_token');

  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login');
  } else {
    next();
  }
});

export default router;
```

-----

## PART 3: Què passa quan el Token caduca? (Refresh Token)

L'`access_token` caduca ràpidament. Quan ho fa, el backend retorna un error **401 Unauthorized**. Utilitzarem el `refresh_token` per demanar un token nou automàticament sense molestar l'usuari.

Modifiqueu el fitxer `src/services/api.js` per afegir un **Interceptor de RESPONSE**:

```javascript
// ... Codi anterior de l'api.js ...

api.interceptors.response.use(
  (response) => {
    return response; 
  },
  async (error) => {
    const originalRequest = error.config;

    // Si l'error és 401 i no estàvem ja reintentant...
    if (error.response && error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true; 

      const refreshToken = localStorage.getItem('refresh_token');
      
      if (refreshToken) {
        try {
          // Demanem un token nou
          const response = await axios.post('http://localhost:8000/api/v1/token/refresh/', {
            refresh: refreshToken
          });

          // Actualitzem l'emmagatzematge
          const newAccessToken = response.data.access;
          localStorage.setItem('access_token', newAccessToken);

          // Refem la petició fallida amb el nou token
          originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;
          return api(originalRequest);

        } catch (refreshError) {
          console.error("La sessió ha caducat del tot. Fes login.");
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login'; 
          return Promise.reject(refreshError);
        }
      }
    }
    return Promise.reject(error);
  }
);

export default api;
```

-----

## PART 4: Tasques fora del laboratori (Treball Autònom)

Durant la sessió hem protegit únicament el model d'Usuaris. Ara és el vostre torn d'aplicar la seguretat a la resta de l'aplicació per fer-la totalment robusta i preparar el terreny per al procés de compra.

### Taula de Permisos Recomanats

Apliqueu aquestes regles utilitzant el mètode `get_permissions()` als vostres respectius ViewSets:

| Model / Endpoint | Mètode | Acció a protegir | Permís a aplicar |
| :--- | :--- | :--- | :--- |
| **User** | POST | Registrar-se (`create`) | `AllowAny` (Obert a tothom) |
| **User** | GET, PUT | Veure/Editar perfil | `IsAuthenticated` + `IsSelfOrAdmin` |
| **Event** | GET | Llistar / Veure catàleg | `AllowAny` |
| **Event** | POST, PUT, DEL | Crear / Editar esdeveniment | `IsAuthenticated` + `IsOwnerOrAdmin` |
| **Compra / Order** | POST | Fer un pagament | `IsAuthenticated` |
| **Compra / Order** | GET | Historial de compres | `IsAuthenticated` + `IsOwnerOrAdmin` |

### Llista de Tasques:

1.  **Vincular Esdeveniments i Usuaris:** Aneu al vostre model `Event` i afegiu un camp `creador = models.ForeignKey(User, on_delete=models.CASCADE)`. Executeu les migracions (`makemigrations` i `migrate`).
2.  **Crear el permís `IsOwnerOrAdmin`:** Al fitxer `permissions.py`, creeu aquesta nova regla. És gairebé idèntica a `IsSelfOrAdmin`, però en lloc de comparar l'usuari amb l'objecte (`obj == request.user`), heu de comparar l'usuari amb el creador de l'objecte (`obj.creador == request.user`).
3.  **Aplicar la taula de permisos al Backend:** Aneu al vostre `EventViewSet` (i posteriors) i implementeu la funció `get_permissions()` com heu après a fer amb els usuaris.
4.  **Actualitzar els Tests:** Tots els tests de creació d'esdeveniments o edició de dades fallaran. Modifiqueu-los perquè utilitzin `self.client.force_authenticate(user=usuari_prova)` abans de fer les accions.
5.  **Registre d'Usuaris al Frontend:** Creeu una vista `RegisterView.vue` amb un formulari que faci una crida POST (sense token) a l'endpoint de creació d'usuaris perquè els visitants es puguin donar d'alta.
