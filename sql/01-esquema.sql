-- Ejecutar en la base storeml_database desde Cloud SQL Studio como administrador.
-- Exactamente cuatro tablas de la aplicación. No crea usuarios Google ficticios.
BEGIN;

CREATE TABLE IF NOT EXISTS public.usuarios (
  google_sub TEXT PRIMARY KEY CHECK (length(google_sub) BETWEEN 1 AND 255),
  email TEXT NOT NULL UNIQUE CHECK (email = lower(email) AND email ~ '^[^[:space:]@]+@gmail[.]com$'),
  registrado_en TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  cuota_minuto BIGINT NOT NULL DEFAULT 0 CHECK (cuota_minuto >= 0),
  cuota_usos INTEGER NOT NULL DEFAULT 0 CHECK (cuota_usos BETWEEN 0 AND 30),
  UNIQUE (google_sub, email)
);

CREATE TABLE IF NOT EXISTS public.modelos (
  id INTEGER PRIMARY KEY CHECK (id BETWEEN 10000000 AND 99999999),
  nombre TEXT NOT NULL CHECK (length(nombre) > 0),
  area TEXT NOT NULL CHECK (area IN ('Mercado Inmobiliario','Telecomunicaciones','Minería','Forestal')),
  descripcion TEXT NOT NULL DEFAULT 'Calculadora que suma los tres inputs.',
  archivo TEXT NOT NULL CHECK (archivo ~ '^inference/modelos/(inmobiliario|telecomunicaciones|mineria|forestal)/[a-z_]+[.]py$'),
  activo BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS public.permisos (
  email TEXT NOT NULL CHECK (email = lower(email) AND email ~ '^[^[:space:]@]+@gmail[.]com$'),
  modelo_id INTEGER NOT NULL REFERENCES public.modelos(id),
  usuario_id TEXT,
  habilitado BOOLEAN NOT NULL DEFAULT TRUE,
  creado_en TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (email, modelo_id),
  -- NULL reserva el permiso por Gmail antes del primer login.
  -- Cuando se vincula, Google subject y email deben pertenecer al mismo registro.
  FOREIGN KEY (usuario_id, email) REFERENCES public.usuarios(google_sub, email)
    ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS public.solicitudes (
  usuario_id TEXT NOT NULL REFERENCES public.usuarios(google_sub) ON DELETE CASCADE,
  modelo_id INTEGER NOT NULL REFERENCES public.modelos(id),
  estado TEXT NOT NULL DEFAULT 'pending' CHECK (estado IN ('pending','approved','rejected')),
  creado_en TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  actualizado_en TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (usuario_id, modelo_id)
);

CREATE INDEX IF NOT EXISTS permisos_usuario_idx ON public.permisos(usuario_id);
COMMIT;
