-- Crear primero el usuario PostgreSQL storeml_app desde la interfaz de Cloud SQL.
-- Ejecutar este archivo como postgres en la base storeml_database.
BEGIN;
DO $$ BEGIN
  IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'cloudsqlsuperuser') THEN
    EXECUTE 'REVOKE cloudsqlsuperuser FROM storeml_app';
  END IF;
END $$;
ALTER ROLE storeml_app NOCREATEDB NOCREATEROLE;
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM storeml_app;
GRANT CONNECT ON DATABASE storeml_database TO storeml_app;
GRANT USAGE ON SCHEMA public TO storeml_app;
GRANT SELECT ON public.usuarios, public.modelos, public.permisos, public.solicitudes TO storeml_app;
GRANT INSERT ON public.usuarios, public.solicitudes TO storeml_app;
GRANT UPDATE (email, cuota_minuto, cuota_usos) ON public.usuarios TO storeml_app;
GRANT UPDATE (usuario_id) ON public.permisos TO storeml_app;
GRANT UPDATE (estado, actualizado_en) ON public.solicitudes TO storeml_app;
COMMIT;
