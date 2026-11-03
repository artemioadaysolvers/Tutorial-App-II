"""Valida variables de Actions y genera el archivo de entorno público de Cloud Run."""
import argparse
import json
import os
from pathlib import Path
import re

PATTERNS={
    'GCP_PROJECT_ID':r'[a-z][a-z0-9-]{4,28}[a-z0-9]',
    'GCP_REGION':r'[a-z]+-[a-z]+[0-9]+',
    'GCP_WIF_PROVIDER':r'projects/[0-9]+/locations/global/workloadIdentityPools/[a-z0-9-]+/providers/[a-z0-9-]+',
    'GCP_DEPLOY_SERVICE_ACCOUNT':r'[a-z0-9-]+@[a-z0-9-]+\.iam\.gserviceaccount\.com',
    'ARTIFACT_REPOSITORY':r'[a-z][a-z0-9-]{0,62}',
    'INSTANCE_CONNECTION_NAME':r'[a-z][a-z0-9-]+:[a-z]+-[a-z]+[0-9]+:[a-z][a-z0-9-]+',
    'GOOGLE_WEB_CLIENT_ID':r'[A-Za-z0-9._-]+\.apps\.googleusercontent\.com',
    'DB_PASSWORD_SECRET':r'[a-zA-Z0-9_-]+',
    'DB_PASSWORD_SECRET_VERSION':r'[1-9][0-9]*',
}

def validate(environ):
    values={name:environ.get(name,'') for name in PATTERNS}
    invalid=[name for name,pattern in PATTERNS.items() if not re.fullmatch(pattern,values[name])]
    if invalid:
        raise ValueError('Configura las variables de repositorio: '+', '.join(invalid))
    if not values['GCP_DEPLOY_SERVICE_ACCOUNT'].endswith('@'+values['GCP_PROJECT_ID']+'.iam.gserviceaccount.com'):
        raise ValueError('La cuenta de despliegue debe pertenecer al proyecto configurado')
    if values['INSTANCE_CONNECTION_NAME'].split(':')[0]!=values['GCP_PROJECT_ID']:
        raise ValueError('Cloud SQL debe pertenecer al proyecto configurado')
    return values

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--env-file');args=parser.parse_args()
    try:
        values=validate(os.environ)
        if args.env_file:
            url=os.getenv('INFERENCE_URL','')
            if not re.fullmatch(r'https://[a-z0-9-]+\.[a-z0-9.-]+',url):
                raise ValueError('La URL desplegada del motor no es HTTPS válida')
            config=dict(APP_ENV='production',DB_NAME='storeml_database',DB_USER='storeml_app',
                INSTANCE_CONNECTION_NAME=values['INSTANCE_CONNECTION_NAME'],
                GOOGLE_WEB_CLIENT_ID=values['GOOGLE_WEB_CLIENT_ID'],INFERENCE_URL=url)
            Path(args.env_file).write_text(json.dumps(config,indent=2),'utf-8')
        print('Configuración de despliegue validada')
    except ValueError as error:
        raise SystemExit(str(error))
