'''
Created on May 21, 2013

@author: kidio
'''
'''
Created on Mar 22, 2013

@author: kidio
'''
import pyodbc as msdb

CLIP_CATE_CODE = 5
MOVIE_CATE_COTE = 2
MUSIC_MVCLIP_CATE_CODE = 4
SOURCE_TYPE_CODE = 1

cate_code = 0
#MAke the MSSQL connection
conn_ms = msdb.connect('DRIVER=FreeTDS;SERVER=117.103.196.39;PORT=1433;DATABASE=tv.go.vn;UID=tv.go.vn;PWD=goTV!@#;TDS_Version=8.0;')
cursor_ms = conn_ms.cursor()

 
# Lists the tables in demo

myGetQuery_movie = "select  top 1 * from view_ListMovies"


    # Execute the SQL query and get the response
cursor_ms.execute(myGetQuery_movie)
response = cursor_ms.fetchall()
 
list_colums = []
for row in cursor_ms.columns(table='view_ListMovies'):
    list_colums.append(str(row.column_name))
print list_colums

# Loop through the response and print table names
for row in response:
    for key, value in enumerate(row):
        print list_colums[key]
        print str(value)
        print "-----"


    
conn_ms.close()
    



