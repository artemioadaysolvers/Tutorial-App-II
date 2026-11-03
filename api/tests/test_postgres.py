import json
import os
from pathlib import Path
import unittest
from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient
from sqlalchemy import create_engine,text
from automind_api.app import create_app
from automind_api.auth import Identity
from automind_api.repository import PostgresRepository

ROOT=Path(__file__).resolve().parents[2]
URL=os.getenv('TEST_DATABASE_URL')

@unittest.skipUnless(URL,'Define TEST_DATABASE_URL apuntando a una base PostgreSQL de pruebas vacía')
class PostgresTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine=create_engine(URL,pool_size=1,max_overflow=0)
        with cls.engine.connect() as db:
            existing=db.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE' ")).all()
        if existing:
            cls.engine.dispose()
            raise RuntimeError('Usa una base de pruebas vacía; estas pruebas no borran datos existentes')
        cls.script('01-esquema.sql');cls.script('02-catalogo-y-accesos.sql')
        cls.repo=PostgresRepository(cls.engine)
        cls.user=Identity('google-artem','artemioaday@gmail.com')
        cls.other=Identity('google-other','otro@gmail.com')

    @classmethod
    def script(cls,name):
        raw=cls.engine.raw_connection()
        try:
            raw.driver_connection.autocommit=True
            cur=raw.cursor();cur.execute((ROOT/'sql'/name).read_text('utf-8'));cur.close()
        finally:
            raw.driver_connection.autocommit=False
            raw.close()

    @classmethod
    def tearDownClass(cls):cls.engine.dispose()

    def query(self,sql,**params):
        with self.engine.begin() as db:
            result=db.execute(text(sql),params)
            return result.mappings().all() if result.returns_rows else []

    def test_01_exactly_four_tables_and_initial_access(self):
        self.assertEqual([r['table_name'] for r in self.query("SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE' ORDER BY table_name")],['modelos','permisos','solicitudes','usuarios'])
        self.assertEqual(len(self.repo.catalog()),24)
        self.assertEqual(len(self.query('SELECT * FROM usuarios')),0)
        expected=json.loads((ROOT/'catalog/models.json').read_text('utf-8'))
        self.assertEqual([dict(row) for row in self.query('SELECT id,archivo FROM modelos ORDER BY id')],[dict(id=m['id'],archivo=m['archivo']) for m in expected])
        ids=json.loads((ROOT/'catalog/initial-access.json').read_text('utf-8'))[0]['modelIds']
        self.assertEqual(self.repo.grant(self.user.email)['modelIds'],ids)

    def test_02_constraints(self):
        for sql,params in [
            ('INSERT INTO permisos (email,modelo_id) VALUES (:email,:id)',dict(email=self.user.email,id=99999999)),
            ('INSERT INTO permisos (email,modelo_id) VALUES (:email,:id)',dict(email=self.user.email,id=10000001)),
            ("INSERT INTO modelos (id,nombre,area,archivo) VALUES (:id,'X','Minería','inference/modelos/mineria/cart.py')",dict(id=1234567)),
            ('UPDATE modelos SET archivo=:path WHERE id=10000002',dict(path='../../other.py'))]:
            with self.assertRaises(Exception):self.query(sql,**params)

    def test_03_verified_registration_and_binding(self):
        self.repo.register(self.user);self.repo.register(self.user);self.repo.register(self.other)
        self.assertEqual(len(self.query('SELECT * FROM usuarios')),2)
        self.assertEqual(self.repo.grant(self.user.email)['subject'],self.user.sub)
        self.assertIsNone(self.repo.grant(self.other.email))
        with self.assertRaises(Exception):self.query('UPDATE permisos SET usuario_id=:sub WHERE email=:email',sub=self.other.sub,email=self.user.email)

    def test_04_requests_do_not_grant_access(self):
        self.repo.request(self.other,10000002);self.repo.request(self.other,10000002)
        self.assertEqual(self.repo.requested(self.other),[10000002])
        self.assertEqual(len(self.query('SELECT * FROM solicitudes')),1)
        self.assertIsNone(self.repo.grant(self.other.email))

    def test_05_parameterization_and_revocation(self):
        self.assertIsNone(self.repo.grant("' OR 1=1 --"))
        self.query('UPDATE permisos SET habilitado=FALSE WHERE email=:email AND modelo_id=10000002',email=self.user.email)
        self.assertNotIn(10000002,self.repo.grant(self.user.email)['modelIds'])
        self.query('UPDATE permisos SET habilitado=TRUE WHERE email=:email AND modelo_id=10000002',email=self.user.email)

    def test_06_quota_is_atomic(self):
        with ThreadPoolExecutor(max_workers=8) as pool:
            accepted=list(pool.map(lambda _:self.repo.consume(self.other),range(40)))
        self.assertEqual(sum(accepted),30)
        self.assertEqual(self.query('SELECT cuota_usos FROM usuarios WHERE google_sub=:sub',sub=self.other.sub)[0]['cuota_usos'],30)

    def test_07_api_with_sql_repository(self):
        app=create_app(self.repo,lambda _:self.user,lambda id,inputs:dict(modelId=id,values=[sum(inputs.values())],unit='unidades',demo=True))
        with TestClient(app) as client:
            headers={'Authorization':'Bearer valid'};payload={'inputs':dict(input1=10,input2=-3,input3=.5)}
            result=client.post('/v1/models/10000002/predict',headers=headers,json=payload)
            self.assertEqual(result.status_code,200);self.assertEqual(result.json()['values'],[7.5])
            self.query('UPDATE permisos SET habilitado=FALSE WHERE email=:email AND modelo_id=10000002',email=self.user.email)
            self.assertEqual(client.post('/v1/models/10000002/predict',headers=headers,json=payload).status_code,403)

    def test_08_limited_application_role(self):
        self.query('CREATE ROLE automind_app LOGIN')
        self.query('INSERT INTO permisos (email,modelo_id) VALUES (:email,10000001)',email='reservado@gmail.com')
        raw=self.engine.raw_connection()
        try:
            raw.driver_connection.autocommit=True;cur=raw.cursor()
            cur.execute('SELECT current_database()');name=cur.fetchone()[0]
            self.assertTrue(name.replace('_','').isalnum())
            cur.execute((ROOT/'sql/03-privilegios-app.sql').read_text('utf-8').replace('ON DATABASE storeml_database',f'ON DATABASE "{name}"'))
            cur.execute('SET ROLE automind_app');cur.close()
        finally:
            raw.driver_connection.autocommit=False
            raw.close()
        try:
            user=Identity('google-reserved','reservado@gmail.com')
            self.repo.register(user);self.repo.request(user,10000002)
            self.assertEqual(self.repo.grant(user.email)['subject'],user.sub)
            self.assertTrue(self.repo.consume(user))
            for sql in ["INSERT INTO permisos (email,modelo_id) VALUES ('otro@gmail.com',10000001)",
                        'UPDATE permisos SET habilitado=TRUE','DELETE FROM usuarios','CREATE TABLE public.extra (id INTEGER)']:
                with self.assertRaises(Exception):self.query(sql)
        finally:self.query('RESET ROLE')

if __name__=='__main__':unittest.main()
