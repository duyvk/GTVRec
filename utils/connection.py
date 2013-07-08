'''
Created on Jul 3, 2013

@author: kidio
'''
import pyodbc as msdb

def SQL_connection ():
    conn_ms = msdb.connect('DRIVER=FreeTDS;SERVER=117.103.196.39;PORT=1433;DATABASE=tv.go.vn;UID=tv.go.vn;PWD=goTV!@#;TDS_Version=8.0;')
    return conn_ms