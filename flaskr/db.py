from psycopg2 import connect
# Local hosting
# BASE_URL = "http://127.0.0.1:8000/api/"

# Production hosting
BASE_URL = "https://pg-flask-rest.herokuapp.com/api/"


def get_conn_db():
    db_name = 'd2rqo5613re182'
    user_name = 'ntrfylfbzpwopk'
    host_name = 'ec2-174-129-240-67.compute-1.amazonaws.com'
    passwd = '8b2413c9d453644338573e79a45949c75db862fca0c10c4190e3d50f82fef780'
    port_num = '5432'
    conn = connect(dbname=db_name, user=user_name, host=host_name, password=passwd, port=port_num)
    return conn
