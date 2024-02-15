'''Creates a sql database'''

import sqlite3

conn = sqlite3.connect('lso.db')
c = conn.cursor()

#Just name and info 
c.execute('''CREATE TABLE lawyers
             (name text, info text)''')

conn.commit()

conn.close()
