# A lightweight, easy to use, customizable Highscore Server.

No login, no personal data! Creating a leaderboard is as simple as **just clicking a button.** Then you will get an upload key and a download key. You can upload and download data by just **sending GET requests to different api and passing data only through the url**. *POST request, query parameters, etc. are not needed at all*.  
You can set sorting order for each column of the table **seperatly through the url only**, no pre-configuration required. Every time you request data you can **specify the data sorting order.**    
As it uses sqlite so no connection to external database server is required. As it uses a local file database so it is somewhat faster than using an external database server.   
**To run it on replit just press the RUN button.**  
**Else you can run it by :**   
*Development Server ->*   
```bash
python3 ServerDev.py
```
*Production Server ->*     
```bash
python3 ServerProd.py
```
For more information about stroing highscores visit [this page](https://scoremadeeasy.souptikdatta.repl.co/help).   
[Try it here](https://scoremadeeasy.souptikdatta.repl.co/).  
****
**Useful Information** - *This project is inspired from a similar srevice called dreamlo. But my project has certain useful improvements. For example :*  
- In dreamlo during downloading the data all the columns were sorted in Descending order but in my version you can sort each column in different orders thus giving you more control for creating more complex relations in the leaderboard.
* During inserting dreamlo only considered the first integer column i.e if the new value of the **first integer column** *is greater* than the present value of that column then only the row would be updated. But in my version not only you are given multiple column support but you can also specify that whether you want to insert the greater one or  the lesser one from the url only during each request.   

**Dreamlo is also a great product, but my requirements were not fulfilled by dreamlo and so I created my own more customizable leaderboard server.**
****    
**Some challanges that I faced while working with sqlite and how I tackled them -**   
- Sqlite does not have support for auto time column update with new timestamps on an UPDATE query. So I have to write triggers to update time after each update.  
  ```sql
  CREATE TRIGGER IF NOT EXISTS updatethetime 
  AFTER UPDATE
  ON Highscores
  FOR EACH ROW
  BEGIN
    UPDATE Highscores SET lastupdated=CURRENT_TIMESTAMP WHERE clientid=NEW.clientid AND playerid=NEW.playerid;
  END;
  ```
- Sqlite does not have OUTER JOIN or RIGHT JOIN. So, to perform an outer join I have to perform two Left Joins, once A with B and then B with A and then do a Union.  

*But ultimately this was a fun learning experience.*    
****
**N.B** - *I made this in about 2 days for a game that I was working on during a Game Jam. It is ready to use, but there may be some optimization or security issues. If any one finds any issues then feel free to raise an issue and let me know.*    
Thank you.