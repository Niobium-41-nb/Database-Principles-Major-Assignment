"""
数据库配置模块

该模块包含数据库连接配置，使用Windows身份验证连接SQL Server数据库。
配置参数包括服务器地址、数据库名称等。
"""

# Windows 身份验证配置
DB_SERVER = 'localhost'  # 或您的SQL Server实例名，如 'localhost\\SQLEXPRESS'
DB_NAME = 'OJ'
# 不需要用户名和密码，使用Windows身份验证