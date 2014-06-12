#
# This Program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
# 
# This Program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING.  If not, write to
# the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# http://www.gnu.org/copyleft/gpl.html
# 

### import modules
import datetime
import mysql.connector
from mysql.connector import errorcode
import os
import socket
import xbmc
import xbmcaddon

### get addon info
__addon__       = xbmcaddon.Addon(id='service.playerlog')
__addonid__     = __addon__.getAddonInfo('id')
__addonname__   = __addon__.getAddonInfo('name')
__version__     = __addon__.getAddonInfo('version')
# __author__      = __addon__.getAddonInfo('author')
# __addonpath__   = __addon__.getAddonInfo('path')
# __addonprofile__= xbmc.translatePath(__addon__.getAddonInfo('profile')).decode('utf-8')
# __icon__        = __addon__.getAddonInfo('icon')
# __localize__    = __addon__.getLocalizedString

__SLEEP_TIME__ = 1000


class PlayerlogDB:

    dbconnection = None

    def __init__(self):
        import mysql.connector

    def __del__(self):
        if self.dbconnection is not None:
           self.dbconnection.close

    def setHostname(self, hostname):
        self.hostname = hostname

    def setPort(self, port):
        self.port = port

    def setDatabase(self, database):
        self.database = database

    def setCredentials(self, username, password):
        self.username = username
        self.password = password

    def insertLogEntry(self, hostname, userprofile, action, filename, title):
        try:
            dbconnection = mysql.connector.Connect(host = self.hostname, 
                                                    port = int(self.port),
                                                    database = self.database,
                                                    user = self.username,
                                                    password = self.password,
                                                    charset = 'utf8',
                                                    collation = 'utf8_general_ci')

            cursor = dbconnection.cursor()
            cursor.execute('SET NAMES utf8;')
            cursor.execute('SET CHARACTER SET utf8;')
            cursor.execute('SET character_set_connection=utf8;')


            query = ("INSERT INTO log (hostname, userprofile, action, filename, title) "
                    "VALUES (%s, %s, %s, %s, %s)")
            data = (hostname, userprofile, action, filename, title)
            cursor.execute(query, data)
            dbconnection.commit()
            cursor.close()
            dbconnection.close()
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
              log("Incorrect MySQL username or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
              log("Database does not exists")
            else:
              log(err)

class PlayerLogService(xbmc.Player):

    playerLogDB = None
    hostname = ""
    userprofile = ""
    filename = ""
    title = ""

    def __init__(self, parent=None):
        xbmc.Player.__init__(self)
        self.parent = parent
        self.hostname = socket.gethostname()

    def setPlayerLogDB(self, playerLogDB):
        self.db = playerLogDB

    def logEntry(self, action):
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        entry = ('timestamp: %s, hostname: %s, userprofile: %s, action: %s, filename: %s, title: %s' 
                    %(now, self.hostname, self.userprofile, action, self.filename, self.title))
        log(entry)
        self.db.insertLogEntry(self.hostname, self.userprofile, action, self.filename, self.title)

    def onPlayBackStarted(self):
        self.userprofile = xbmc.getInfoLabel('System.ProfileName')
        try:
            self.filename = self.getPlayingFile()
            if self.isPlayingVideo():
                self.title = self.getVideoInfoTag().getTitle()
            elif self.isPlayingAudio:
                self.getMusicInfoTag().getTitle()
            else:
                self.title = ""
        except Exception, err:
            log(str(err))
        self.logEntry('onPlayBackStarted()')

    def onPlayBackEnded(self):
        self.logEntry('onPlayBackEnded()')
        self.userprofile = ""
        self.filename = ""
        self.title = ""

    def onPlayBackStopped(self):
        self.logEntry('onPlayBackStopped()')
        self.userprofile = ""
        self.filename = ""
        self.title = ""

    def onPlayBackPaused(self):
        self.logEntry('onPlayBackPaused()')

    def onPlayBackResumed(self):
        self.logEntry('onPlayBackResumed()')


def log(message):
    xbmc.log(__addonid__ + ': ' + message)


if (__name__ == "__main__"):

    log('Starting: ' + __addonname__ + ' v' + __version__)

    dbhostname = __addon__.getSetting('hostname')
    port = __addon__.getSetting('port')
    database = __addon__.getSetting('database')
    username = __addon__.getSetting('username')
    password = __addon__.getSetting('password')

    playerLogDB = PlayerlogDB()
    playerLogDB.setHostname(dbhostname)
    playerLogDB.setPort(port)
    playerLogDB.setDatabase(database)
    playerLogDB.setCredentials(username, password)

    playerLogService = PlayerLogService()
    if (dbhostname != ""):
        playerLogService.setPlayerLogDB(playerLogDB)
    else:
        log('Database hostname not configured for profile: ' + xbmc.getInfoLabel('System.ProfileName'))

    while (not xbmc.abortRequested):
        xbmc.sleep(__SLEEP_TIME__)

    del playerLogService

    log('Stopped: ' + __addonname__ + ' v' + __version__)

