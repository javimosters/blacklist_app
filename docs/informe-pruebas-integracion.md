# Informe: Pruebas de integración con Postman/Newman — blacklist_app

**Repositorio:** https://github.com/javimosters/blacklist_app
**Servicio cubierto:** `blacklist_email` (microservicio Flask + PostgreSQL de blacklist global de emails)
**Equipo:** Javier Rafael Carballo Ballesta, Jesus David Sanchez Villarreal, Marco Antonio Rhenals Agresoth, Valentina Olascoaga Teherán

## 1. Objetivo

Automatizar la validación de los endpoints del servicio `blacklist_email` mediante una colección de Postman ejecutada con Newman, e integrar esa ejecución como un job de GitHub Actions (`pruebas_integracion`) que corra en cada push/pull request hacia `master`.

## 2. Endpoints cubiertos

El servicio expone el blueprint de blacklist bajo el prefijo `/blacklists`:

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| GET | `/blacklists/ping` | No | Health check del servicio |
| POST | `/blacklists` | Bearer token | Crea un registro de email en la blacklist |
| GET | `/blacklists/<email>` | Bearer token | Consulta si un email está en la blacklist |

## 3. Paso a paso realizado

### 3.1 Creación de la colección de Postman

Se creó la colección `postman/Blacklist_API.postman_collection.json` (formato Postman Collection v2.1) con 6 requests:

1. **Ping** — `GET /blacklists/ping`, valida código `200`.
2. **Crear email - válido** — `POST /blacklists` con un email, `app_uuid` y motivo válidos, autenticado con Bearer token. Valida `200`, `201` o `409` (409 se acepta porque el email de prueba puede quedar ya registrado de una corrida anterior; el objetivo es validar que el endpoint responde correctamente en ambos casos, no que cada corrida cree un registro nuevo).
3. **Consultar email - válido** — `GET /blacklists/<email>` sobre el mismo email, autenticado. Valida `200`.
4. **Crear email - sin token** — igual que el punto 2 pero sin header de autenticación. Valida `401`.
5. **Crear email - inválido** — `POST /blacklists` con un email mal formado. Valida `400`.
6. **Consultar email - sin token** — igual que el punto 3 pero sin autenticación. Valida `401`.

Cada request incluye un script `pm.test()` que verifica el código de estado de la respuesta.

### 3.2 Exportación del `.json` de la colección

La colección se exportó tal cual queda en Postman (Export → Collection v2.1) y se guardó como `postman/Blacklist_API.postman_collection.json` en la raíz del repositorio. La autenticación Bearer y las URLs (`http://localhost:5001/...`) quedan guardadas dentro de cada request, por lo que el archivo no depende de un environment aparte.

### 3.3 Ejecución local con Newman

Para correr la colección de forma local:

```bash
# 1. Instalar Newman (una sola vez)
npm install -g newman

# 2. Levantar el servicio y su base de datos con Docker Compose
cd blacklist_app
docker compose up -d --build

# 3. Esperar a que responda (unos segundos)
curl http://localhost:5001/blacklists/ping

# 4. Desde la raíz del repositorio, ejecutar la colección
cd ..
newman run "./postman/Blacklist_API.postman_collection.json"
```

Newman corre las 6 requests en orden, imprime en consola el resultado de cada `pm.test` y retorna código de salida distinto de cero si alguna aserción falla — esto es lo que permite usarlo como *gate* en CI.

> Nota: si se corre la colección varias veces seguidas localmente sin reiniciar la base de datos, el email de prueba (`malo@test.com`) queda registrado desde la primera corrida. Por diseño, el test de "Crear email - válido" acepta tanto `201` (creado) como `409` (ya existía), así que esto no rompe la prueba. Para partir de una base de datos limpia se puede correr `docker compose down -v` antes de repetir.

### 3.4 Job `pruebas_integracion` en GitHub Actions

Se agregó el workflow `.github/workflows/pruebas_integracion.yml` con el job `pruebas_integracion`, que:

1. Hace checkout del repositorio.
2. Instala Node.js 20 y luego Newman (`npm install -g newman`).
3. Genera el archivo `.env` del servicio con el `BEARER_TOKEN` guardado como *secret* del repositorio (`secrets.BEARER_TOKEN`), para no exponer el token en el código.
4. Levanta la aplicación y su base de datos PostgreSQL con `docker compose up -d --build` (el mismo `docker-compose.yml` usado en el despliegue local).
5. Espera, con un loop de `curl`, a que `/blacklists/ping` responda antes de continuar.
6. Ejecuta la colección de Postman con Newman contra el servicio recién levantado.
7. Si algo falla, imprime los logs de los contenedores para poder diagnosticar.
8. Al final (pase o falle), apaga los contenedores con `docker compose down`.

El job corre automáticamente en cada `push` y `pull_request` hacia `master`.

**Importante:** para que el job funcione, hay que crear el secret `BEARER_TOKEN` en el repositorio (`Settings → Secrets and variables → Actions → New repository secret`) con el mismo valor que está escrito en la autenticación Bearer de la colección de Postman. Si no coincide, las requests que requieren autenticación fallarán con `401` en vez del código esperado.

## 4. Estructura de archivos agregados al repositorio

```
.
├── .github/
│   └── workflows/
│       └── pruebas_integracion.yml
├── postman/
│   └── Blacklist_API.postman_collection.json
├── docs/
│   └── informe-pruebas-integracion.md
└── blacklist_app/          # código del servicio (sin cambios)
```

## 5. Notas y siguientes pasos

- El token usado en la colección de Postman es de pruebas; en el `.env` real de cada integrante del equipo se mantiene su propio `BEARER_TOKEN` para desarrollo local.
- Si se agregan nuevos endpoints al servicio, la colección debe actualizarse en Postman y volver a exportarse sobre este mismo archivo.
- El workflow depende de que el secret `BEARER_TOKEN` esté configurado en el repositorio; sin él, todas las requests autenticadas devolverán `401`.
