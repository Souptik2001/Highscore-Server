import sqlite3

try:
  with sqlite3.connect('database.db') as db:
    with db as cur:
      clients = cur.execute('SELECT *FROM Highscores').fetchall()
      print(clients)
except Exception as e:
  print(e)



  #https://highscore-server.souptikdatta.repl.co/download/<downloadid>