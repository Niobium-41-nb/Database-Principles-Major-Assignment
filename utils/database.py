import pyodbc
import config

def get_db_connection():
    """获取数据库连接 - Windows身份验证"""
    DB_CONFIG = {
        'server': config.DB_SERVER,
        'database': config.DB_NAME,
        'trusted_connection': 'yes',
        'driver': '{ODBC Driver 17 for SQL Server}'
    }
    
    conn_str = f"DRIVER={DB_CONFIG['driver']};SERVER={DB_CONFIG['server']};DATABASE={DB_CONFIG['database']};Trusted_Connection=yes"
    try:
        return pyodbc.connect(conn_str)
    except Exception as e:
        print(f"数据库连接失败: {str(e)}")
        raise