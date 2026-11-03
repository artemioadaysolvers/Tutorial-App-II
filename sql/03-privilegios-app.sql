-- Crear primero el usuario PostgreSQL automind_app desde la interfaz de Cloud SQL.
-- Ejecutar este archivo como postgres en la base automind.
BEGIN;
DO $$ BEGIN
  IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'cloudsqlsuperuser') THEN
    EXECUTE 'REVOKE cloudsqlsuperuser FROM automind_app';
  END IF;
END $$;
ALTER ROLE automind_app NOCREATEDB NOCREATEROLE;
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM automind_app;
GRANT CONNECT ON DATABASE storeml_database TO automind_app;
GRANT USAGE ON SCHEMA public TO automind_app;
GRANT SELECT ON public.usuarios, public.modelos, public.permisos, public.solicitudes TO automind_app;
GRANT INSERT ON public.usuarios, public.solicitudes TO automind_app;
GRANT UPDATE (email, cuota_minuto, cuota_usos) ON public.usuarios TO automind_app;
GRANT UPDATE (usuario_id) ON public.permisos TO automind_app;
GRANT UPDATE (estado, actualizado_en) ON public.solicitudes TO automind_app;
COMMIT;
