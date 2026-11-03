import time
from sqlalchemy import text

def model_row(row):
    return dict(id=row['id'], name=row['nombre'], area=row['area'], description=row['descripcion'],
        active=row['activo'], algorithm='suma', formula='y=x_1+x_2+x_3', unit='unidades', demo=True,
        fields=[dict(key=f'input{i}', label=f'Input {i}', min=-1e12, max=1e12) for i in (1,2,3)])

class PostgresRepository:
    def __init__(self, engine):
        self.engine = engine

    def register(self, user):
        with self.engine.begin() as db:
            db.execute(text('''INSERT INTO public.usuarios (google_sub,email) VALUES (:sub,:email)
                ON CONFLICT (google_sub) DO UPDATE SET email=EXCLUDED.email
                WHERE usuarios.email IS DISTINCT FROM EXCLUDED.email'''),vars(user))
            db.execute(text('''UPDATE public.permisos SET usuario_id=:sub
                WHERE email=:email AND usuario_id IS NULL'''),vars(user))

    def catalog(self):
        with self.engine.connect() as db:
            return [model_row(row) for row in db.execute(text('SELECT * FROM public.modelos WHERE activo=TRUE ORDER BY id')).mappings()]

    def model(self, model_id):
        with self.engine.connect() as db:
            row = db.execute(text('SELECT * FROM public.modelos WHERE id=:id'),dict(id=model_id)).mappings().first()
            return model_row(row) if row else None

    def grant(self, email):
        with self.engine.connect() as db:
            rows = db.execute(text('''SELECT email,modelo_id,usuario_id FROM public.permisos
                WHERE email=:email AND habilitado=TRUE ORDER BY modelo_id'''),dict(email=email)).mappings().all()
            if not rows:
                return None
            return dict(email=email, enabled=True, subject=next((r['usuario_id'] for r in rows if r['usuario_id']),None),
                modelIds=[r['modelo_id'] for r in rows])

    def request(self, user, model_id):
        with self.engine.begin() as db:
            db.execute(text('''INSERT INTO public.solicitudes (usuario_id,modelo_id) VALUES (:sub,:id)
                ON CONFLICT (usuario_id,modelo_id) DO UPDATE SET estado='pending',actualizado_en=CURRENT_TIMESTAMP
                WHERE solicitudes.estado<>'pending' ''').bindparams(sub=user.sub,id=model_id))

    def requested(self, user):
        with self.engine.connect() as db:
            return list(db.execute(text("SELECT modelo_id FROM public.solicitudes WHERE usuario_id=:sub AND estado='pending' ORDER BY modelo_id"),dict(sub=user.sub)).scalars())

    def consume(self, user):
        with self.engine.begin() as db:
            row = db.execute(text('''UPDATE public.usuarios
                SET cuota_minuto=:minute,cuota_usos=CASE WHEN cuota_minuto=:minute THEN cuota_usos+1 ELSE 1 END
                WHERE google_sub=:sub AND (cuota_minuto<>:minute OR cuota_usos<30) RETURNING google_sub'''),
                dict(minute=int(time.time()//60),sub=user.sub)).first()
            return row is not None
