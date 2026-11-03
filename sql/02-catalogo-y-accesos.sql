-- Pegar en Cloud SQL Studio después de 01-esquema.sql.
-- No sobrescribe cambios manuales ni permisos ya revocados.
BEGIN;
INSERT INTO public.modelos (id,nombre,area,descripcion,archivo,activo) VALUES
  (10000001,'Árbol de Decisión KS','Mercado Inmobiliario','Calculadora de suma para Mercado Inmobiliario. Suma los tres inputs numéricos y devuelve el total. ID: 10000001.','inference/modelos/inmobiliario/ks.py',TRUE),
  (10000002,'Árbol de Decisión CART','Mercado Inmobiliario','Calculadora de suma para Mercado Inmobiliario. Suma los tres inputs numéricos y devuelve el total. ID: 10000002.','inference/modelos/inmobiliario/cart.py',TRUE),
  (10000003,'Red Neuronal','Mercado Inmobiliario','Calculadora de suma para Mercado Inmobiliario. Suma los tres inputs numéricos y devuelve el total. ID: 10000003.','inference/modelos/inmobiliario/red_neuronal.py',TRUE),
  (10000004,'Regresión Lineal Múltiple','Mercado Inmobiliario','Calculadora de suma para Mercado Inmobiliario. Suma los tres inputs numéricos y devuelve el total. ID: 10000004.','inference/modelos/inmobiliario/regresion.py',TRUE),
  (10000005,'Holt Winters','Mercado Inmobiliario','Calculadora de suma para Mercado Inmobiliario. Suma los tres inputs numéricos y devuelve el total. ID: 10000005.','inference/modelos/inmobiliario/holt_winters.py',TRUE),
  (10000006,'Prophet de Meta','Mercado Inmobiliario','Calculadora de suma para Mercado Inmobiliario. Suma los tres inputs numéricos y devuelve el total. ID: 10000006.','inference/modelos/inmobiliario/prophet.py',TRUE),
  (10000007,'Árbol de Decisión KS','Telecomunicaciones','Calculadora de suma para Telecomunicaciones. Suma los tres inputs numéricos y devuelve el total. ID: 10000007.','inference/modelos/telecomunicaciones/ks.py',TRUE),
  (10000008,'Árbol de Decisión CART','Telecomunicaciones','Calculadora de suma para Telecomunicaciones. Suma los tres inputs numéricos y devuelve el total. ID: 10000008.','inference/modelos/telecomunicaciones/cart.py',TRUE),
  (10000009,'Red Neuronal','Telecomunicaciones','Calculadora de suma para Telecomunicaciones. Suma los tres inputs numéricos y devuelve el total. ID: 10000009.','inference/modelos/telecomunicaciones/red_neuronal.py',TRUE),
  (10000010,'Regresión Lineal Múltiple','Telecomunicaciones','Calculadora de suma para Telecomunicaciones. Suma los tres inputs numéricos y devuelve el total. ID: 10000010.','inference/modelos/telecomunicaciones/regresion.py',TRUE),
  (10000011,'Holt Winters','Telecomunicaciones','Calculadora de suma para Telecomunicaciones. Suma los tres inputs numéricos y devuelve el total. ID: 10000011.','inference/modelos/telecomunicaciones/holt_winters.py',TRUE),
  (10000012,'Prophet de Meta','Telecomunicaciones','Calculadora de suma para Telecomunicaciones. Suma los tres inputs numéricos y devuelve el total. ID: 10000012.','inference/modelos/telecomunicaciones/prophet.py',TRUE),
  (10000013,'Árbol de Decisión KS','Minería','Calculadora de suma para Minería. Suma los tres inputs numéricos y devuelve el total. ID: 10000013.','inference/modelos/mineria/ks.py',TRUE),
  (10000014,'Árbol de Decisión CART','Minería','Calculadora de suma para Minería. Suma los tres inputs numéricos y devuelve el total. ID: 10000014.','inference/modelos/mineria/cart.py',TRUE),
  (10000015,'Red Neuronal','Minería','Calculadora de suma para Minería. Suma los tres inputs numéricos y devuelve el total. ID: 10000015.','inference/modelos/mineria/red_neuronal.py',TRUE),
  (10000016,'Regresión Lineal Múltiple','Minería','Calculadora de suma para Minería. Suma los tres inputs numéricos y devuelve el total. ID: 10000016.','inference/modelos/mineria/regresion.py',TRUE),
  (10000017,'Holt Winters','Minería','Calculadora de suma para Minería. Suma los tres inputs numéricos y devuelve el total. ID: 10000017.','inference/modelos/mineria/holt_winters.py',TRUE),
  (10000018,'Prophet de Meta','Minería','Calculadora de suma para Minería. Suma los tres inputs numéricos y devuelve el total. ID: 10000018.','inference/modelos/mineria/prophet.py',TRUE),
  (10000019,'Árbol de Decisión KS','Forestal','Calculadora de suma para Forestal. Suma los tres inputs numéricos y devuelve el total. ID: 10000019.','inference/modelos/forestal/ks.py',TRUE),
  (10000020,'Árbol de Decisión CART','Forestal','Calculadora de suma para Forestal. Suma los tres inputs numéricos y devuelve el total. ID: 10000020.','inference/modelos/forestal/cart.py',TRUE),
  (10000021,'Red Neuronal','Forestal','Calculadora de suma para Forestal. Suma los tres inputs numéricos y devuelve el total. ID: 10000021.','inference/modelos/forestal/red_neuronal.py',TRUE),
  (10000022,'Regresión Lineal Múltiple','Forestal','Calculadora de suma para Forestal. Suma los tres inputs numéricos y devuelve el total. ID: 10000022.','inference/modelos/forestal/regresion.py',TRUE),
  (10000023,'Holt Winters','Forestal','Calculadora de suma para Forestal. Suma los tres inputs numéricos y devuelve el total. ID: 10000023.','inference/modelos/forestal/holt_winters.py',TRUE),
  (10000024,'Prophet de Meta','Forestal','Calculadora de suma para Forestal. Suma los tres inputs numéricos y devuelve el total. ID: 10000024.','inference/modelos/forestal/prophet.py',TRUE)
ON CONFLICT (id) DO NOTHING;

INSERT INTO public.permisos (email,modelo_id,habilitado) VALUES
  ('artemioaday@gmail.com',10000001,TRUE),
  ('artemioaday@gmail.com',10000002,TRUE),
  ('artemioaday@gmail.com',10000003,TRUE),
  ('artemioaday@gmail.com',10000007,TRUE),
  ('artemioaday@gmail.com',10000008,TRUE),
  ('artemioaday@gmail.com',10000009,TRUE),
  ('artemioaday@gmail.com',10000013,TRUE),
  ('artemioaday@gmail.com',10000014,TRUE),
  ('artemioaday@gmail.com',10000015,TRUE),
  ('artemioaday@gmail.com',10000019,TRUE),
  ('artemioaday@gmail.com',10000020,TRUE),
  ('artemioaday@gmail.com',10000021,TRUE)
ON CONFLICT (email,modelo_id) DO NOTHING;
COMMIT;
