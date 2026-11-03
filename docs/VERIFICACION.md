# Verificación del backend Python + PostgreSQL

Fecha: 3 de noviembre de 2026.

## Comprobado

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
- No se probó Cloud SQL, TLS del conector, Secret Manager o IAM en la cuenta del usuario. No se desplegaron recursos ni se realizó login con sus clientes OAuth. Las pruebas de identidad inyectan o simulan el verificador; producción utiliza google-auth.verify_oauth2_token.
- No se generó un APK ni se compiló iOS. La migración cambia el servidor y no los componentes nativos del móvil. La compilación nativa anterior se detuvo por falta de espacio; el último TypeScript y bundle del móvil habían pasado.
- El contenedor Linux no se ejecutó aquí.
- No se ha ejecutado el workflow en GitHub Actions ni se ha probado este despliegue contra Google Cloud. Requiere la configuración inicial del manual, incluyendo IAM, variables y recursos. El PostgreSQL 17 del workflow se ejecutará en GitHub; la verificación SQL local descrita arriba utilizó PGlite.
