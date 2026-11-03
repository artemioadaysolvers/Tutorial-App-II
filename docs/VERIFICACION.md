# Verificación del backend Python + PostgreSQL

Fecha: 3 de noviembre de 2026.

## Comprobado

- En esta actualización pasaron `npm run typecheck`, `npm run bundle:android`, las tres pruebas de configuración y actionlint. Android procesó correctamente el manifiesto y compiló el Kotlin de la aplicación y sus librerías con applicationId/namespace com.storeml.app (`:app:compileDebugKotlin`, BUILD SUCCESSFUL). Se verificaron las clases com.storeml.app.MainActivity y com.storeml.app.MainApplication en el manifiesto generado. Esto no equivale a generar un APK ni a ejecutar el login Google en un dispositivo.
- GitHub Actions 41733568714 terminó con éxito: pruebas con PostgreSQL 17, calculadoras, validación de variables, compilación Docker, OIDC y despliegue de ambos servicios. Se verificaron los resultados de todos sus jobs y pasos en GitHub.
- Backend real https://automind-api-286807177004.southamerica-west1.run.app: GET /v1/catalog, GET /v1/me y POST de predicción sin credenciales respondieron 401 con el mensaje de login Google; GET /v1/me con token inválido también respondió 401. Esto verifica rechazo de esas peticiones, no un login ni una predicción autorizados.
- El certificado debug de GitHub, el archivo local y el incluido en el ZIP coinciden. Huella SHA-1: 5E:8F:16:06:2E:A3:CD:2C:4A:0D:54:78:76:BA:A6:F3:8C:AB:F6:25.

- La configuración de despliegue usa DB_NAME=storeml_database. El SQL de privilegios, sus pruebas y los ejemplos utilizan ese nombre. La instancia de ejemplo es storeml-pg y el repositorio Artifact Registry es storeml.

- API completamente en Python: FastAPI, google-auth, SQLAlchemy, pg8000 y Cloud SQL Python Connector. Se retiraron las fuentes TypeScript, scripts npm y package.json de la API.
- `python -m unittest discover -s tests -v`: 22 pruebas aprobadas en Python. Catorce verifican rutas protegidas, registro de identidad validada, Gmail verificado, IDs numéricos, campos extra, inyección de correo, suma, revocación entre peticiones y durante cálculo, solicitudes, cuota, errores y límite de cuerpo.
- Las ocho pruebas PostgreSQL utilizaron SQLAlchemy/pg8000 por protocolo PostgreSQL contra un servidor PGlite local de QA. Ejecutaron los archivos SQL reales (adaptando solo el nombre de base del test) y verificaron cuatro tablas, 24 rutas, 12 permisos reservados, claves y unicidad, vinculación correcta, solicitudes idempotentes, SQL parametrizado, revocación, cuota de 30/40 y rol limitado.
- Se probó el flujo HTTP Python con repositorio SQL, con una suma autorizada de 7,5 y posterior revocación.
- Modelos Python: tres pruebas aprobadas para 24 archivos independientes, IDs de ocho dígitos, rutas correctas y 72 casos de suma con positivos, negativos, decimales y ceros.
- Los esquemas y privilegios PostgreSQL se mantienen; no se añade una quinta tabla. La app móvil conserva el contrato HTTP existente y sus IDs numéricos.
- GitHub Actions: sintaxis del workflow validada con actionlint 1.7.12. Tres pruebas del validador de variables aprobadas: valores válidos, variables ausentes y rechazo de proyectos incoherentes, versión `latest` y texto inválido.
- El workflow ejecuta las pruebas de API contra PostgreSQL 17 temporal, las calculadoras y la configuración antes del despliegue. Las pull requests no obtienen credenciales de despliegue; solo el job de despliegue en `main` puede solicitar OIDC. Las cuatro acciones están fijadas a SHAs completos verificados en sus repositorios oficiales.
- El manual PDF se actualiza con configuración por interfaz de OIDC, Artifact Registry, variables de GitHub y despliegue automático; se revisan sus páginas renderizadas.

## Límites

- El servidor PGlite fue una herramienta local externa de QA; no es un componente del backend entregado. Las pruebas de integración Python también pueden apuntar a una base PostgreSQL vacía mediante TEST_DATABASE_URL.
- El usuario completó el despliegue en Cloud Run y la configuración de Cloud SQL/Secret Manager desde la consola. Reportó rolcreatedb=false, rolcreaterole=false y ausencia de membresía cloudsqlsuperuser para storeml_app. No se ha realizado aún un login Google real desde Android ni una predicción autorizada en producción. Las pruebas unitarias de identidad usan un verificador inyectado; producción utiliza google-auth.verify_oauth2_token.
- No se generó un APK de publicación ni se compiló iOS. Se actualizan applicationId/namespace y paquetes Kotlin a com.storeml.app. La firma de depuración sigue siendo la del ZIP; el certificado de release y el cliente iOS requieren configuración propia.
- El contenedor Linux no se ejecutó aquí.
- Se verificó la ejecución 41709403113 en GitHub Actions: identidad y todas las etapas de pruebas finalizaron correctamente, incluyendo PostgreSQL 17 de CI. El despliegue se detuvo en Validar variables de despliegue por cinco variables ausentes; no compiló ni publicó imágenes ni se autenticó en Google Cloud.
- Las cuentas de ejecución son storeml-api y storeml-inference; despliega storeml-deploy. El último despliegue exitoso se verificó en GitHub (41733568714), además de las cuatro respuestas HTTP 401 del backend real para peticiones anónimas o con token inválido.
