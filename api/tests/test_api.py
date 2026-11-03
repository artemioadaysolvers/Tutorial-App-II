import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from automind_api.app import create_app
from automind_api.auth import Identity,GoogleVerifier

USER=Identity('google-A','a@gmail.com')
MODEL=dict(id=10000002,active=True,demo=True,fields=[dict(key=f'input{i}',min=-1e12,max=1e12) for i in (1,2,3)])
VALUES={'input1':10,'input2':-3,'input3':.5}
HEADERS={'Authorization':'Bearer valid'}

class Repo:
    def __init__(self):
        self.permission=dict(email=USER.email,subject=USER.sub,enabled=True,modelIds=[MODEL['id']])
        self.users=[];self.pending=[];self.quota=True
    def register(self,user):self.users.append(user)
    def catalog(self):return [MODEL]
    def model(self,id):return MODEL if id==MODEL['id'] else None
    def grant(self,email):return self.permission
    def requested(self,user):return self.pending
    def request(self,user,id):self.pending.append(id)
    def consume(self,user):return self.quota

class ApiTests(unittest.TestCase):
    def setUp(self):
        self.repo=Repo();self.calls=0
        def verify(token):
            if token!='valid':raise ValueError('inválido')
            return USER
        def predict(id,inputs):
            self.calls+=1
            return dict(modelId=id,values=[sum(inputs.values())],unit='unidades',demo=True)
        self.app=create_app(self.repo,verify,predict)
        self.client=TestClient(self.app)
    def tearDown(self):self.client.close()
    def calculate(self,body=None,headers=HEADERS,path='/v1/models/10000002/predict'):
        return self.client.post(path,headers=headers,json=body if body is not None else {'inputs':VALUES})

    def test_all_routes_require_google(self):
        for path in ['/v1/catalog','/v1/me']:
            self.assertEqual(self.client.get(path).status_code,401)
        self.assertEqual(self.calculate(headers={}).status_code,401)
        self.assertEqual(self.client.post('/v1/requests',json={'modelId':10000002}).status_code,401)
        self.assertEqual(self.repo.users,[])

    def test_rejected_token_does_not_register(self):
        self.assertEqual(self.calculate(headers={'Authorization':'Bearer forged'}).status_code,401)
        self.assertEqual(self.repo.users,[])

    def test_exact_google_identity_is_registered(self):
        self.assertEqual(self.client.get('/v1/me',headers=HEADERS).status_code,200)
        self.assertEqual(self.repo.users,[USER])

    def test_missing_disabled_or_other_identity_has_no_permission(self):
        for grant in [None,dict(email=USER.email,enabled=False,modelIds=[10000002]),
                      dict(email='b@gmail.com',enabled=True,modelIds=[10000002]),
                      dict(email=USER.email,subject='other',enabled=True,modelIds=[10000002])]:
            self.repo.permission=grant
            self.assertEqual(self.calculate().status_code,403)
        self.assertEqual(self.calls,0)

    def test_injected_email_extra_fields_and_invalid_numbers_are_rejected(self):
        for body in [{'inputs':VALUES,'email':'b@gmail.com'}, {'inputs':{**VALUES,'gmail':5}},
                     {'inputs':{**VALUES,'input1':True}}, {'inputs':{**VALUES,'input2':None}},
                     {'inputs':{**VALUES,'input1':'10'}}, {'inputs':{**VALUES,'input1':1e13}}]:
            self.assertEqual(self.calculate(body).status_code,400)
        self.assertEqual(self.calls,0)

    def test_numeric_id_format(self):
        for id in ['1234567','123456789','01234567','10000002.0','otro']:
            self.assertEqual(self.calculate(path=f'/v1/models/{id}/predict').status_code,400)
        for id in ['10000002',1234567,123456789,10000002.5,True]:
            self.assertEqual(self.client.post('/v1/requests',headers=HEADERS,json={'modelId':id}).status_code,400)

    def test_sum_and_exact_id(self):
        result=self.calculate()
        self.assertEqual(result.status_code,200)
        self.assertEqual(result.json()['values'],[7.5])
        self.assertEqual(result.json()['modelId'],10000002)
        self.assertEqual(self.calculate(path='/v1/models/10000014/predict').status_code,403)

    def test_revocation(self):
        self.assertEqual(self.calculate().status_code,200)
        self.repo.permission=None
        self.assertEqual(self.calculate().status_code,403)
        self.assertEqual(self.calls,1)

    def test_revocation_during_calculation(self):
        def revoke(id,inputs):
            self.repo.permission=None
            return dict(values=[999],unit='unidades',demo=True)
        self.app.state.predict=revoke
        result=self.calculate()
        self.assertEqual(result.status_code,403)
        self.assertNotIn('values',result.json())

    def test_request_is_not_a_permission(self):
        self.repo.permission=None
        result=self.client.post('/v1/requests',headers=HEADERS,json={'modelId':10000002})
        self.assertEqual(result.status_code,202)
        self.assertEqual(self.repo.pending,[10000002])
        self.assertEqual(self.calculate().status_code,403)

    def test_request_cannot_choose_another_email(self):
        result=self.client.post('/v1/requests',headers=HEADERS,json={'modelId':10000002,'email':'b@gmail.com'})
        self.assertEqual(result.status_code,400)
        self.assertEqual(self.repo.pending,[])

    def test_quota_and_worker_failure(self):
        self.repo.quota=False
        self.assertEqual(self.calculate().status_code,429)
        self.assertEqual(self.calls,0)
        self.repo.quota=True
        def unavailable(*args):raise RuntimeError('falló')
        self.app.state.predict=unavailable
        self.assertEqual(self.calculate().status_code,503)

    def test_disabled_model_and_body_limit(self):
        with patch.dict(MODEL,active=False):self.assertEqual(self.calculate().status_code,404)
        self.assertEqual(self.client.post('/v1/requests',headers=HEADERS,content=b'x'*17000).status_code,413)

class IdentityTests(unittest.TestCase):
    def test_google_claims_require_verified_gmail(self):
        verifier=GoogleVerifier('example.apps.googleusercontent.com')
        for info in [dict(sub='A',email='a@gmail.com',email_verified=False),
                     dict(sub='A',email='a@example.com',email_verified=True),dict(email='a@gmail.com',email_verified=True)]:
            with patch('automind_api.auth.id_token.verify_oauth2_token',return_value=info):
                with self.assertRaises(ValueError):verifier('token')
        with patch('automind_api.auth.id_token.verify_oauth2_token',return_value=dict(sub='A',email='A@gmail.com',email_verified=True)):
            self.assertEqual(verifier('token'),Identity('A','a@gmail.com'))

if __name__=='__main__':unittest.main()
