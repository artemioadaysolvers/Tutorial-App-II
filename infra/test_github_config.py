import unittest
from github_config import validate

class ConfigTests(unittest.TestCase):
    def setUp(self):
        self.env=dict(GCP_PROJECT_ID='automind-demo',GCP_REGION='southamerica-west1',
            GCP_WIF_PROVIDER='projects/123456/locations/global/workloadIdentityPools/github/providers/storeml',
            GCP_DEPLOY_SERVICE_ACCOUNT='storeml-deploy@automind-demo.iam.gserviceaccount.com',
            ARTIFACT_REPOSITORY='storeml',INSTANCE_CONNECTION_NAME='automind-demo:southamerica-west1:storeml-pg',
            GOOGLE_WEB_CLIENT_ID='123-abc.apps.googleusercontent.com',DB_PASSWORD_SECRET='storeml-db-password',
            DB_PASSWORD_SECRET_VERSION='1')
    def test_valid_values(self):self.assertEqual(validate(self.env),self.env)
    def test_missing_variables(self):
        for name in self.env:
            with self.subTest(name=name),self.assertRaises(ValueError):validate({k:v for k,v in self.env.items() if k!=name})
    def test_wrong_projects_or_shell_payloads(self):
        for name,value in [('GCP_PROJECT_ID','x; echo wrong'),('DB_PASSWORD_SECRET_VERSION','latest'),
                           ('GCP_DEPLOY_SERVICE_ACCOUNT','user@another-project.iam.gserviceaccount.com'),
                           ('INSTANCE_CONNECTION_NAME','other-project:southamerica-west1:storeml-pg')]:
            with self.subTest(name=name),self.assertRaises(ValueError):validate({**self.env,name:value})

if __name__=='__main__':unittest.main()
