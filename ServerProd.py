import datetime
import uuid
import math
import sqlite3
import flask
app = flask.Flask('app')
DATABASE_FILE_NAME = 'database.db'

try :
  with sqlite3.connect(DATABASE_FILE_NAME) as db:
    db.execute("CREATE TABLE IF NOT EXISTS Clients ('clientdownloadid' STRING PRIMARY KEY, 'clientsecretid' STRING UNIQUE)")
except Exception as e:
  print(e)

try :
  with sqlite3.connect(DATABASE_FILE_NAME) as db:
    db.execute("CREATE TABLE IF NOT EXISTS Highscores ('clientid' STRING , 'playerid' STRING, 'name1' STRING, 'name2' STRING, 'score1' INTEGER, 'score2' INTEGER, 'score3' INTEGER,     'lastUpdated' TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL, FOREIGN KEY (clientid) REFERENCES Clients(clientdownloadid) ON DELETE CASCADE ON UPDATE NO ACTION)")
    db.execute("""
      CREATE TRIGGER IF NOT EXISTS updatethetime 
      AFTER UPDATE
      ON Highscores
      FOR EACH ROW
      BEGIN
        UPDATE Highscores SET lastupdated=CURRENT_TIMESTAMP WHERE clientid=NEW.clientid AND playerid=NEW.playerid;
      END;
    """)
except Exception as e:
  print(e)


@app.route('/')
def hello_world():
  return flask.render_template('index.html')

@app.route('/<string:client_upload_code>/upload/<string:player_id>/<string:name1>/<string:score1>', methods=('GET',))
@app.route('/<string:client_upload_code>/upload/<string:player_id>/<string:name1>/<string:score1>/<string:name2>', methods=('GET',))
@app.route('/<string:client_upload_code>/upload/<string:player_id>/<string:name1>/<string:score1>/<string:score2>/<string:name2>', methods=('GET',))
@app.route('/<string:client_upload_code>/upload/<string:player_id>/<string:name1>/<string:score1>/<string:score2>/<string:score3>/<string:name2>', methods=('GET',))
@app.route('/<string:client_upload_code>/upload/<string:player_id>/<string:name1>/<string:score1>/<string:score2>', methods=('GET',))
@app.route('/<string:client_upload_code>/upload/<string:player_id>/<string:name1>/<string:score1>/<string:score2>/<string:score3>', methods=('GET',))

def upload(client_upload_code, player_id, name1, score1, score2=None, score3=None, name2=None):

  allIntegerEntries = [score1, score2, score3]
  allIntegerOrders = []
  try:

    for x in range(len(allIntegerEntries)):
      if(allIntegerEntries[x]!=None):
        ascore1 = allIntegerEntries[x].split("@")
        allIntegerEntries[x] = int(ascore1[0])
        if(len(ascore1)>1):
          allIntegerOrders.append(int(ascore1[1]))
        else:
          allIntegerOrders.append(0)
      else:
        allIntegerOrders.append(0)
    # for x in range(len(allIntegerOrders)):
    #   print(allIntegerOrders[x])
  except Exception as e:
    return flask.jsonify(
      error="1",
      errorReason="There is something wrong with the parameters you passed : " + str(e),
        success="0"
      )

  try:
        with sqlite3.connect(DATABASE_FILE_NAME) as db:
          with db as cur:
            db.set_trace_callback(print)

            client_present_check = cur.execute("SELECT * FROM Clients WHERE clientsecretid=?", [client_upload_code]).fetchall()

            if(len(client_present_check) == 0):
              return flask.jsonify(
                error="1",
                errorReason="Client not present",
                success="0"
              )

            # Actually only one instance will be present
            allInstancesOfThisPlayer = cur.execute("""
            SELECT * FROM
            (SELECT 
            *
            FROM 
            Clients LEFT JOIN Highscores ON Clients.clientdownloadid = Highscores.clientid
            UNION ALL
            SELECT 
            *
            FROM 
            Highscores LEFT JOIN Clients ON Clients.clientdownloadid=Highscores.clientid)
            WHERE clientsecretid=? AND playerid=?
            """, [client_upload_code, player_id]).fetchall()

            if(len(allInstancesOfThisPlayer)==0):
              # New Entry
              cur.execute("INSERT INTO Highscores('clientid', 'playerid', 'name1', 'name2', 'score1', 'score2', 'score3') VALUES(?, ?, ?, ?, ?, ?, ?)", [client_present_check[0][0], player_id, name1, name2, allIntegerEntries[0], allIntegerEntries[1], allIntegerEntries[2]])
            else:
              old_playerdata = allInstancesOfThisPlayer[0]

              x = -1
              changeValuesToOldEntries = 0

              while x < len(allIntegerEntries)-1:
                x = x + 1
                if(allIntegerEntries[x]!=None and old_playerdata[x+6]!=None):
                  if(allIntegerEntries[x] == old_playerdata[x+6]):
                    if(x==len(allIntegerEntries)-1) : changeValuesToOldEntries=1
                    continue

                  if(allIntegerOrders[x]==0):
                    if(allIntegerEntries[x]<old_playerdata[x+6]):
                      changeValuesToOldEntries = 1
                  else:
                    if(allIntegerEntries[x]>old_playerdata[x+6]):
                      changeValuesToOldEntries = 1
                  break
                else:
                  if(allIntegerEntries[x]==None):
                    changeValuesToOldEntries=1
                    break

              print(changeValuesToOldEntries)

              if(changeValuesToOldEntries==1):
                return flask.jsonify(
                  error="0",
                  errorReason="Success but nothing to change",
                  success="1"
                )

              cur.execute("""UPDATE Highscores SET 'clientid'=?, 'playerid'=?, 'name1'=?, 'name2'=?, 'score1'=?, 'score2'=?, 'score3'=? WHERE clientid=? AND playerid=?""", [allInstancesOfThisPlayer[0][0], player_id, name1, name2, allIntegerEntries[0], allIntegerEntries[1], allIntegerEntries[2], allInstancesOfThisPlayer[0][0], player_id])
            cur.commit()

        return flask.jsonify(
          error="0",
          errorReason="",
          success="1"
        )
  except Exception as e:
      return flask.jsonify(
        error="1",
        errorReason=str(e),
        success="0"
      )

# 0 : descending
# 1 or any other : ascending
@app.route('/<string:client_download_code>/download', methods=('GET',))
@app.route('/<string:client_download_code>/download/<int:sort_score1>/<int:sort_score2>/<int:sort_score3>', methods=('GET',))
def download(client_download_code, sort_score1=None, sort_score2=None, sort_score3=None):
    sortClause_score1 = "DESC"
    sortClause_score2 = "DESC"
    sortClause_score3 = "DESC"

    if(sort_score1!=None):
      if(sort_score1!=0):
        sortClause_score1 = "ASC"
      if(sort_score2!=0):
        sortClause_score2 = "ASC"
      if(sort_score3!=0):
        sortClause_score3 = "ASC"

    try:
      with sqlite3.connect(DATABASE_FILE_NAME) as db:
        with db as cur:
          db.set_trace_callback(print)
          players = []
          playerIndex = 0

          ## OUTER JOIN is not present in sqlite so instead of this query I am using the query written below it
          # players_cur = cur.execute("""SELECT 
          # Clients.clientdownloadid, Highscores.playerid, Highscores.name1, Highscores.name2, Highscores.score1, Highscores.score2, Highscores.score3 
          # FROM 
          # Clients FULL OUTER JOIN Highscores ON Clients.clientdownloadid=Highscores.clientid
          # WHERE Clients.clientdownloadid=?""", [client_download_code])
          # players_raw = players_cur.fetchall()

          # players_cur = cur.execute("""SELECT * FROM
          # (SELECT 
          # Clients.clientdownloadid, Highscores.playerid, Highscores.name1, Highscores.name2, Highscores.score1, Highscores.score2, Highscores.score3 
          # FROM 
          # Clients LEFT JOIN Highscores ON Clients.clientdownloadid = Highscores.clientid
          # UNION ALL
          # SELECT 
          # Clients.clientdownloadid, Highscores.playerid, Highscores.name1, Highscores.name2, Highscores.score1, Highscores.score2, Highscores.score3 
          # FROM 
          # Highscores LEFT JOIN Clients ON Clients.clientdownloadid=Highscores.clientid)
          # WHERE clientdownloadid=?""", [client_download_code])

          finalQuery = "SELECT Clients.clientdownloadid, Highscores.playerid, Highscores.name1, Highscores.name2, Highscores.score1, Highscores.score2, Highscores.score3, Highscores.lastUpdated FROM Clients LEFT JOIN Highscores ON Highscores.clientid=Clients.clientdownloadid WHERE clientdownloadid=? ORDER BY score1 " + sortClause_score1 + ", score2 " + sortClause_score2 + ", score3 " + sortClause_score3

          players_cur = cur.execute(finalQuery, [client_download_code])
          players_raw = players_cur.fetchall()

          if(len(players_raw)==0):

            finalQuery = "SELECT Clients.clientsecretid, Highscores.playerid, Highscores.name1, Highscores.name2, Highscores.score1, Highscores.score2, Highscores.score3, Highscores.lastUpdated FROM Clients LEFT JOIN Highscores ON Highscores.clientid=Clients.clientdownloadid WHERE clientsecretid=? ORDER BY score1 " + sortClause_score1 + ", score2 " + sortClause_score2 +  ", score3 " + sortClause_score3

            players_raw = cur.execute(finalQuery, [client_download_code]).fetchall() #Here we are checking that the downloadid which we are porividing may be secret id

            if(len(players_raw)==0):
              return flask.jsonify(
                error="1",
                errorReason="The Client Id you provided is not present",
                success="0"
            )

            print("!! Client providing upload ID for downloading !!")

          for player_raw in players_raw:
            if(player_raw[1]==None): continue
            players.append({
              "clientid" : player_raw[0], #this will not be given
              "playerid" : player_raw[1],
              "name1" : player_raw[2],
              "name2" : player_raw[3],
              "score1" : player_raw[4],
              "score2" : player_raw[5],
              "score3" : player_raw[6],
              "lastUpdated" : player_raw[7]
            })
            playerIndex = playerIndex + 1
      return flask.jsonify(players)
    except Exception as e:
      return flask.jsonify(
        error="1",
        errorReason=str(e),
        success="0"
      )

@app.route('/createnewclient', methods=('POST',))
def createNewClient():
  try:
    with sqlite3.connect(DATABASE_FILE_NAME) as db:
      with db as cur:
        code_seed = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        generated_client_secret_upload_id = "upload_" + str(uuid.uuid5(uuid.NAMESPACE_DNS, code_seed + "_secret_upload"))
        generated_client_download_id = "download_" + str(uuid.uuid5(uuid.NAMESPACE_DNS, code_seed + "download"))

        cur.execute("INSERT INTO Clients VALUES(?, ?)", [generated_client_download_id, generated_client_secret_upload_id])
        cur.commit()
    return flask.redirect(flask.url_for('dashboard', clientuploadid=generated_client_secret_upload_id, clientdownload=generated_client_download_id))
  except Exception as e:
      return flask.jsonify(
        error="1",
        errorReason=str(e),
        success="0"
      )

@app.route('/<string:clientuploadid>/dashboard', methods=('GET',))
@app.route('/<string:clientuploadid>/dashboard/<int:sort_score1>/<int:sort_score2>/<int:sort_score3>', methods=('GET',))
def dashboard(clientuploadid, sort_score1=None, sort_score2=None, sort_score3=None):

  sortClause_score1 = "DESC"
  sortClause_score2 = "DESC"
  sortClause_score3 = "DESC"

  if(sort_score1!=None):
    if(sort_score1!=0):
      sortClause_score1 = "ASC"
    if(sort_score2!=0):
      sortClause_score2 = "ASC"
    if(sort_score3!=0):
      sortClause_score3 = "ASC"

  try:
    players = []
    playerIndex = 0
    with sqlite3.connect(DATABASE_FILE_NAME) as db:
      with db as cur:
        db.set_trace_callback(print)
        finalQuery = "SELECT * FROM Clients LEFT JOIN Highscores ON Highscores.clientid=Clients.clientdownloadid WHERE clientsecretid=? ORDER BY score1 " + sortClause_score1 + ", score2 " + sortClause_score2 + ", score3 " + sortClause_score3

        players_raw = cur.execute(finalQuery, [clientuploadid]).fetchall()

        for player_raw in players_raw:
          if(player_raw[2]==None): continue
          players.append({
              "playerid" : player_raw[3],
              "name1" : player_raw[4],
              "name2" : player_raw[5],
              "score1" : player_raw[6],
              "score2" : player_raw[7],
              "score3" : player_raw[8],
              "lastUpdated" : player_raw[9]
            })
          playerIndex = playerIndex + 1

        if(len(players_raw)==0):
          return flask.jsonify(
            error="1",
            errorReason="The Client id you provided is not present",
            success="0"
          )

          
        return flask.render_template('dashboard.html', public_id=players_raw[0][0], secret_id=players_raw[0][1], leaderboard=players)
  except Exception as e:
    return flask.jsonify(
        error="1",
        errorReason="Database error : " + str(e),
        success="0"
      )



@app.route('/<string:clientuploadid>/delete/<string:playerid>', methods=('GET',))
def delete(clientuploadid, playerid):
  try:
    with sqlite3.connect(DATABASE_FILE_NAME) as db:
      with db as cur:
        
        client_data = cur.execute("SELECT * FROM Clients WHERE clientsecretid=?", [clientuploadid]).fetchall()

        if(len(client_data)==0):
          return flask.jsonify(
            error="1",
            errorReason="Client id you provided is not present",
            success="0"
          )
        client_download_id = client_data[0][0]
        cur.execute('DELETE FROM Highscores WHERE clientid=? AND playerid=?', [client_download_id, playerid])
        cur.commit()
      return flask.jsonify(
        error="0",
        errorReason="",
        success="1"
      )
  except Exception as e:
      return flask.jsonify(
        error="1",
        errorReason=str(e),
        success="0"
      )


@app.route('/<string:clientuploadid>/clear', methods=('GET',))
def clear(clientuploadid):
  try:
    with sqlite3.connect(DATABASE_FILE_NAME) as db:
      with db as cur:
        
        client_data = cur.execute("SELECT * FROM Clients WHERE clientsecretid=?", [clientuploadid]).fetchall()

        if(len(client_data)==0):
          return flask.jsonify(
            error="1",
            errorReason="Client id you provided is not present",
            success="0"
          )
        client_download_id = client_data[0][0]
        cur.execute('DELETE FROM Highscores WHERE clientid=?', [client_download_id])
        cur.commit()
      return flask.jsonify(
        error="0",
        errorReason="",
        success="1"
      )
  except Exception as e:
      return flask.jsonify(
        error="1",
        errorReason=str(e),
        success="0"
      )

@app.route('/help', methods=('GET',))
def helpRoute():
  return flask.render_template('help.html')


from waitress import serve
serve(app, host="0.0.0.0", port=8080)
