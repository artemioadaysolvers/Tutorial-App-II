# AutoMind / React Native + TypeScript / PostgreSQL

App Android/iOS con Google Gmail, Store, solicitudes y acceso por ID. Las 24 calculadoras suman tres inputs; cada una tiene su propio `.py` y un `MODEL_ID` entero único de ocho dígitos (10000001 a 10000024). La estética mantiene Skia, RaTeX y tipografía de máquina de escribir. Sin WebView ni AppView.

## Una base y cuatro tablas

La base PostgreSQL `automind` tiene exactamente cuatro tablas de aplicación en `public`:

- `usuarios`: subject Google verificado, Gmail, fecha y contador de cuota.
- `modelos`: ID, nombre, área, descripción, ruta `archivo` y estado activo.
- `permisos`: Gmail, modelo y subject vinculado; clave única por Gmail/modelo y claves foráneas.
- `solicitudes`: usuario, modelo, estado y fechas; clave única por usuario/modelo.

No se utiliza Firestore ni Firebase. Los IDs de modelo son números, no strings, en JSON y en los permisos. La app solo llama al backend; no recibe credenciales SQL ni GitHub. Todo el backend propio está en Python y SQL. TypeScript se mantiene en React Native.

## Archivos y configuración manual

- `sql/01-esquema.sql`: las cuatro tablas y restricciones.
- `sql/02-catalogo-y-accesos.sql`: 24 modelos con sus rutas y los 12 permisos de artemioaday@gmail.com (KS, CART y Red Neuronal por área). No crea un usuario Google ficticio.
- `sql/03-privilegios-app.sql`: permisos SQL mínimos para `automind_app`.
- `api/`: backend Python con FastAPI, SQLAlchemy, pg8000, consultas parametrizadas y conector Python oficial de Cloud SQL.
- `inference/modelos/<área>/<modelo>.py`: los 24 archivos Python independientes.
- `inference/registry.py`: lista fija de IDs y módulos permitidos.
- `mobile/`: React Native con proyectos Android e iOS.
- `docs/GUIA-GOOGLE-CLOUD.pdf` y `.md`: manual completo de creación por interfaz, Cloud SQL Studio, secretos, OAuth, despliegue, edición de datos y compilación.

En Cloud SQL Studio, como administrador de `automind`, ejecuta los tres archivos SQL en orden después de crear el usuario `automind_app`. El manual contiene todos los pasos. Los archivos iniciales conservan cambios existentes y no vuelven a habilitar permisos revocados.

## Rutas del repositorio privado

Ejemplo: ID `10000002`, `archivo = inference/modelos/inmobiliario/cart.py`, `MODEL_ID = 10000002`. El contenedor ejecuta su copia desplegada. La columna documenta la ubicación; no permite importar una ruta arbitraria enviada por el teléfono. Si mueves un archivo, ajusta registro, columna y despliegue.

## Conexión de producción

Cuenta de servicio de API con Cloud SQL Client y acceso al secreto de su contraseña. Variables `INSTANCE_CONNECTION_NAME`, `DB_NAME=automind`, `DB_USER=automind_app`, `GOOGLE_WEB_CLIENT_ID`, `INFERENCE_URL`; `DB_PASSWORD` referenciado desde Secret Manager. No usar `postgres` como usuario de aplicación. El motor Python queda privado y separado de PostgreSQL.

Para ejecutar la API usa `uvicorn automind_api.main:app --host 0.0.0.0 --port 8080` después de configurar las variables de conexión y OAuth. Para desarrollo puede usarse `DATABASE_URL=postgresql+pg8000://...` con `APP_ENV` distinto de production. En Cloud Run el conector oficial es obligatorio.

El rol SQL de la API no puede editar el catálogo, otorgar permisos ni crear tablas. Solo registra identidades Google verificadas, vincula reservas de ese Gmail, gestiona solicitudes y aplica la cuota. Revocación y permisos se consultan en cada cálculo y antes de devolverlo.

## Verificación y compilación

En `api`, con Python 3.10/3.11: `pip install -r requirements-test.txt` y `python -m unittest discover -s tests -v`. Las 14 pruebas de API/identidad no necesitan PostgreSQL. Las ocho de integración se activan con `TEST_DATABASE_URL` hacia una base PostgreSQL de pruebas vacía; nunca uses tu base productiva para ellas. Se verificaron localmente con pg8000 y PGlite; no conectan con tu Cloud SQL. En `inference`: `python -m unittest test_models.py` verifica los 24 archivos y sus sumas. El servidor Python requiere `requirements.txt`.

Para Android: Node 22.11+, JDK 17, SDK/Build Tools 36, NDK 27.1.12297006. Extrae en ruta corta, completa `mobile/src/config.ts`, ejecuta `npm ci`, `npm run typecheck` y compila desde Android Studio o `mobile/android/gradlew.bat`. Firma release con tus propiedades `AUTOMIND_*`. El manual cubre APK/AAB, SHA-1 y configuración iOS.

La compilación nativa anterior no terminó por espacio de disco; no se entrega APK. No se desplegaron recursos en tu cuenta. Consulta `docs/VERIFICACION.md` para las comprobaciones realizadas y sus límites.
