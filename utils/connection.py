'''
Created on Jul 3, 2013

@author: kidio
'''
import pyodbc as msdb

def SQL_connection ():
    conn_ms = msdb.connect('DRIVER=FreeTDS;SERVER=117.103.196.39;PORT=1433;DATABASE=tv.go.vn;UID=tv.go.vn;PWD=goTV!@#;TDS_Version=8.0;')
    return conn_ms

def bongngo_SQL_connection():
    conn_ms = msdb.connect('DRIVER=FreeTDS;SERVER=117.103.196.38;PORT=1433;DATABASE=unofficial;UID=unofficial;PWD=unofficial;TDS_Version=8.0;')
    return conn_ms

if __name__ == "__main__":
    conn_ms = bongngo_SQL_connection()
    cursor = conn_ms.cursor()
    cursor.execute("select * from view_ListMovies")
    
    for movie in cursor.fetchall():
        print movie[1]
    