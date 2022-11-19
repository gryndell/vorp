# vorpdb.py Database functions for Virtual Operation Recording Program
# Copyright(C) 2022 Alfred Pengelly

#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.

#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.

#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import json
import sqlite3
import requests
from passlib.hash import sha256_crypt
import datetime

# Global Variables
sqliteFile = os.environ["HOME"] + '/vorp.sqlite'
logName = './vorp.log'
logFile = open(logName, 'a', encoding='utf-8')
logFile.close()


def logEvent(iEvent):
    now = datetime.datetime.now()
    logFile = open(logName, 'a', encoding='utf-8')
    logFile.write("{}: {}\n".format(now.strftime("%F %H:%M:%S"), iEvent))
    logFile.close()


def pw_verify(iPass):
    try:
        myConn = sqlite3.connect(sqliteFile)
    except Exception as e:
        logEvent("Connection Error: {}".format(str(e)))
        return False
    myQuery = "SELECT Password FROM Control"
    myCurr = myConn.cursor()
    try:
        myCurr.execute(myQuery)
    except Exception as e:
        logEvent("Query: {}".format(myQuery))
        logEvent("Error: {}".format(str(e)))
        return False
    myPass = myCurr.fetchone()[0]
    if sha256_crypt.verify(iPass, myPass):
        return True
    else:
        logEvent("Password Validation Failed!")
        return False


def run_query(iQuery, iArgs):
    try:
        myCon = sqlite3.connect(sqliteFile)
    except Exception as e:
        logEvent("Connection Error: {}".format(str(e)))
        return ()
    try:
        myCur = myCon.cursor()
    except Exception as e:
        logEvent("Cursor Error: {}".format(str(e)))
        return ()
    try:
        myCur.execute(iQuery, iArgs)
    except Exception as e:
        logEvent("Query: {}".format(iQuery))
        logEvent("Error: {}".format(str(e)))
        return ()
    # myCon.commit()
    oRows = myCur.fetchall()
    return oRows


# Test if a given record is already loaded
def isLoaded(iCur, iTable, iId, iOp, iComp, iTask):
    # Use testQuery to check whether record already exists
    testResult = tuple()
    if iTable == 'operationHdr':
        testQuery = """
            SELECT * FROM operationHdr WHERE id = ? AND op = ?
            """
        try:
            iCur.execute(testQuery, (iId, iOp))
        except Exception as e:
            logEvent("Query: {}".format(testQuery))
            logEvent("Args: {}".format((iId, iOp)))
            logEvent("Error: {}".format(str(e)))
            return True
        testResult = iCur.fetchone()
    if iTable == 'operationDtl':
        testQuery = """
            SELECT * FROM operationDtl WHERE id = ? AND op = ? AND
            component = ? AND task = ?
            """
        try:
            iCur.execute(testQuery, (iId, iOp, iComp, iTask))
        except Exception as e:
            logEvent("Query: {}".format(testQuery))
            logEvent("Args: {}".format((iId,
                                        iOp,
                                        iComp,
                                        iTask)))
            logEvent("Error: {}".format(str(e)))
            return 0
        testResult = iCur.fetchone()
    if testResult is not None and len(testResult) > 0:
        return True
    else:
        return False
    # end of isLoaded


def fetchData():
    myId = ''
    myOp = 0
    myComp = ''
    myTask = ''
    # Prevent attempt to load record that already exists,
    # violating index
    try:
        myCon = sqlite3.connect(sqliteFile)
    except Exception as e:
        logEvent("Connection Error: {}".format(str(e)))
        return ()
    try:
        myCur = myCon.cursor()
    except Exception as e:
        logEvent("Cursor Error: {}".format(str(e)))
        return ()
    try:
        myResult = myCur.execute("SELECT url_input FROM Control")
        url_input = myResult.fetchone()[0]
    except Exception as e:
        logEvent("Failed to retrieve input URL. {}".format(str(e)))
        return 0
    try:
        response = requests.get(url_input, headers={'User-Agent': 'Mozilla'})
    except Exception as e:
        logEvent("Request Failure: {}".format(str(e)))
        return 0

    myData = json.loads(response.text)
    myRecords = 0
    try:
        myCon = sqlite3.connect(sqliteFile)
    except Exception as e:
        logEvent("Connection Error: {}".format(str(e)))
        return 0
    try:
        myCur = myCon.cursor()
    except Exception as e:
        logEvent("Cursor Error: {}".format(str(e)))
        return 0
    for tableName in (myData):
        for record in myData[tableName]:
            myQuery1 = "INSERT INTO '" + tableName + "' ("
            myQuery2 = ' VALUES ('
            # First argument is actually the table name
            myFieldList = [tableName]
            myValueList = []
            firstField = True
            for field in record:
                # Need to find out if this record has already been loaded
                # So keep track of id, op, component and task
                if field == 'id':
                    myId = record[field]
                if field == 'op':
                    myOp = record[field]
                if field == 'component':
                    myComp = record[field]
                if field == 'task':
                    myTask = record[field]
                if firstField:
                    myQuery1 = myQuery1 + "'" + field + "'"
                    myQuery2 = myQuery2 + '?'
                    firstField = False
                else:
                    myQuery1 = myQuery1 + ", '" + field + "'"
                    myQuery2 = myQuery2 + ', ?'
                myFieldList.append(field)
                myValueList.append(record[field])
            myQuery = myQuery1 + ')' + myQuery2 + ')'
            myArgs = tuple(myValueList)
            if not isLoaded(myCur, tableName, myId, myOp, myComp, myTask):
                try:
                    myCur.execute(myQuery, myArgs)
                except Exception as e:
                    logEvent("Query: {}".format(myQuery))
                    logEvent("Args: {}".format(myArgs))
                    logEvent("Error: {}".format(str(e)))
                    return 0
                try:
                    myCon.commit()
                except Exception as e:
                    logEvent("Commit Error: {}".format(str(e)))
                    return 0
                myRecords = myRecords + 1
    return myRecords
