import os
from sqlalchemy import create_engine, text

def open_database():
    connector = None
    url = os.getenv('DATABASE_URL')
    options = dict(pool_size=5, max_overflow=0, pool_timeout=10, pool_recycle=1800, pool_pre_ping=True)
    if os.getenv('APP_ENV') != 'production' and url:
        if not url.startswith('postgresql+pg8000://'):
            raise ValueError('DATABASE_URL debe utilizar postgresql+pg8000://')
        engine = create_engine(url, **options)
    else:
        from google.cloud.sql.connector import Connector, IPTypes
        values = {name: os.getenv(name) for name in ['INSTANCE_CONNECTION_NAME','DB_NAME','DB_USER','DB_PASSWORD']}
        if not all(values.values()):
            raise ValueError('Configura la conexión Cloud SQL y el secreto DB_PASSWORD')
        connector = Connector(refresh_strategy='lazy')
        def connect():
            return connector.connect(values['INSTANCE_CONNECTION_NAME'], 'pg8000',
                user=values['DB_USER'], password=values['DB_PASSWORD'], db=values['DB_NAME'],
                ip_type=IPTypes.PUBLIC, timeout=10)
        engine = create_engine('postgresql+pg8000://', creator=connect, **options)
    try:
        with engine.connect() as connection:
            connection.execute(text('SELECT 1'))
    except Exception:
        engine.dispose()
        if connector:
            connector.close()
        raise
    def close():
        engine.dispose()
        if connector:
            connector.close()
    return engine, close
