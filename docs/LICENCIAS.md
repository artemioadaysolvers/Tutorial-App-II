# Componentes y procedencia

- Se conserva la fuente Latin Modern Mono 12 del ZIP suministrado por el usuario, con su licencia GUST junto al archivo de fuente.
- Android/iOS parten de `@react-native-community/template@0.85.3`; su licencia se conserva en `mobile/LICENSE-TEMPLATE`.
- React Native, React, Skia, RaTeX y Google Sign-In incluyen sus licencias en los paquetes npm instalados.
- El servidor de calculadoras utiliza FastAPI, Pydantic y Uvicorn, con sus licencias en los paquetes Python.
- Los 24 archivos de cálculo de esta versión contienen una suma simple. No se distribuyen librerías de aprendizaje automático, datos de entrenamiento ni pesos.

La API Python utiliza FastAPI, SQLAlchemy, pg8000, google-auth, requests, CacheControl y el conector Python oficial de Cloud SQL. Sus licencias se distribuyen en los paquetes Python. PGlite se utilizó como herramienta externa de QA y no es una dependencia del backend entregado.
