import sqlite3
import datetime
import re

database = None
cursor = None




def connect()->None:
    '''Connects to the specified database and sets the global variable'''
    global database, cursor
    database = sqlite3.connect("classes.db")
    cursor = database.cursor()

def toMilitaryTime(timeIn:str,timeOut:str)->{datetime.time}:
    '''Converts two strings to military time'''
    isAfterNoon = 'p' in timeOut.lower()
    #strip of unnecessary items
    timeOne = timeIn.strip()
    timeTwo = timeOut.strip()
    if isAfterNoon:
        timeTwo = timeTwo.split('p')[0]
    #get the delta
    timeOne = timeOne.split(':')
    timeTwo = timeTwo.split(':')
    timeOne = datetime.time(hour = int(timeOne[0]), minute = int(timeOne[1]))
    timeTwo = datetime.time(hour = int(timeTwo[0]), minute = int(timeTwo[1]))
    delta = timeTwo.hour - timeOne.hour
    if isAfterNoon or delta < 0:
        if delta < 0:
            return {'timeIn':timeOne, 'timeOut':timeTwo.replace(hour = timeTwo.hour + 12)}
        else:
            return {'timeIn': timeOne.replace(hour=timeOne.hour + 12), 'timeOut': timeTwo.replace(hour=timeTwo.hour + 12)}
    else:
        return {'timeIn':timeOne, 'timeOut':timeTwo}

def finalsToDateandTime(dateTime:str)->{datetime.datetime,datetime.time}:
    '''Converts string into a date and time'''
    monthsNum = {
        'jan': 1,
        'feb': 2,
        'mar': 3,
        'apr': 4,
        'may': 5,
        'june':6,
        'nov': 11,
        'dec': 12,
    }
    data = re.search(r'(\w{3}),\s(\w{3})\s(\d{1,2}),\s(\d{1,2}:\d{2})-(\d{1,2}:\d{2})([a|p]m)',dateTime.lower())
    data = list(data.groups())
    realTime = toMilitaryTime(data[3], data[4] + data[5])
    date = datetime.datetime(
        year = datetime.datetime.today().year,
        month = monthsNum[data[1]],
        day = int(data[2]),
        hour = realTime["timeIn"].hour,
        minute = realTime["timeIn"].minute
    )
    timeOut = datetime.time(
        hour = realTime["timeOut"].hour,
        minute = realTime["timeOut"].minute
    )
    return {'dateTime': date, 'endTime': timeOut}

def toReadable(data: tuple,title:str)->tuple:
    '''Pulls data out of tupple and converts into dict'''
    #TODO:Clean this up so there is less conversions going back and forth
    master = {
        "department":None,
        "course_id":None,
        "course_name":None,
        "course_code":None,
        "Type":None,
        "section":None,
        "units":None,
        "professor":None,
        "daysOfWeek":None,
        "start_time":None,
        "end_time":None,
        "location":None,
        "final":None,
        "max":None,
        "enrolled":None,
        "waitlist":None,
        "requested":None,
        "restrictions":None,
        "status":None,
        "year": None,
        "term": None
    }
    #convert the title
    titleData = title.split('_')
    master['department'] = titleData[0]
    master['course_id'] = titleData[1]
    master["course_name"] = "_".join(titleData[2:])

    #checks to see if we have the waitlist info
    isWaitlist = len(data) == 16
    #this means that it has had a waitlist option
    index = 0
    listTup = list(data)
    for masterIndex in ["course_code","type","section","units","professor","daysOfWeek","time","location","final","max","enrolled","waitlist", "requested", "restrictions","status", "year", "term"]:
        if (masterIndex == "waitlist" and isWaitlist) or masterIndex != "waitlist":
            if masterIndex == "final":
                theGoods = finalsToDateandTime(listTup[index])
                master["final_datetime"] = theGoods['dateTime']
                master['final_endtime'] = theGoods['endTime']
            elif masterIndex == "time":
                time = toMilitaryTime(listTup[index], listTup[index + 1])
                index += 1
                master['start_time'] = time['timeIn']
                master['end_time'] = time['timeOut']
            else:
                master[masterIndex] = listTup[index]

            index += 1
        else:
            master[masterIndex] = None


    return master

def organizeData(data:dict)->tuple:
    '''converts the dict into the correct order to insert into db'''
    return (data["department"],data["course_id"],data["course_name"],data["course_code"],data["type"],data["section"],data["units"],data["professor"],data["daysOfWeek"],str(data["start_time"]),str(data["end_time"]),data["location"],str(data["final_datetime"]),str(data["final_endtime"]),data["max"],data["enrolled"],data["waitlist"],data["requested"],data["restrictions"],data["status"],data['year'], data['term'])

def insertSingle(data1:dict)->None:
    '''Given a list of data will insert all valid info into the db and return a list of the data that was invalid'''
    global cursor,database
    cursor.execute("INSERT INTO classHistory  VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",organizeData(data1))
    database.commit()

def insertMany(data1:[dict])->None:
    '''Inserts all the dicts in the list into the DB'''
    global cursor
    organized = [organizeData(x) for x in data1]
    cursor.executemany("INSERT INTO classHistory  VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", organized)
    database.commit()

def readAll()->None:
    '''Returns a list of everything in the db'''
    global cursor
    return [x for x in cursor.execute("SELECT * FROM classHistory")]

def getSpecific(specifics:dict)->[tuple]:
    '''Give specifics for wheres like year:2017 and term:3'''
    global cursor
    specifics = [list(x) for x in specifics.items()]
    answer = "AND".join(["`{}` = '{}'".format(x[0], x[1]) for x in specifics])
    print("SELECT * FROM classHistory WHERE " + answer)
    return [x for x in cursor.execute("SELECT * FROM classHistory WHERE " + answer)]





if __name__ == "__main__":
    pass
    # print(toReadable(('50000', 'LEC', 'A', '4', 'WHITELEY, J.', 'TuTh', '15:30', '16:50p', 'SSLH 100', 'Tue, Dec 12, 4:00-6:00pm', '399', '395', ' 2', ' 579', 'OPEN','2017', '1'),"yes_31_haha"))
    #print(toMilitaryTime('12:00', '4:00pm'))
    #print(finalsToDateandTime('Fri, Mar 24, 10:00-12:00pm'))

    # #Start Block
    # connect()
    # theData = toReadable(('50005', 'LEC', 'A', '4', 'WHITELEY, J.', 'TuTh', '2:43', '3:50p', 'SSLH 100', 'Tue, Dec 12, 4:00-6:00pm', '399', '395', ' 2', ' 579', 'OPEN', '2017', '1'),"yes_31_haha")
    # insertSingle(theData)
    # cursor.close()
    # #EndBlock

    ##Testing Military Time
    # print((toMilitaryTime('3:50', '4:30p')))

    # #Test for inserting many
    # connect()
    # theData = [
    #     toReadable(('90785', 'LEC', 'A', '4', 'WHITELEY, J.', 'TuTh', '2:43', '3:50p', 'SSLH 100', 'Tue, Dec 12, 4:00-6:00pm', '399', '395', ' 2', ' 579', 'OPEN', '2019', '3'),"yes_31_haha"),
    #     toReadable(('67005', 'LEC', 'A', '4', 'WHITELEY, J.', 'TuTh', '2:43', '3:50p', 'SSLH 100', 'Tue, Dec 12, 4:00-6:00pm', '399', '395', ' 2', ' 579', 'OPEN', '2014', '1'),"no_45_gors")
    # ]
    # insertMany(theData)
    # cursor.close()

    # #Test for readAll()
    # connect()
    # print(readAll())
    # cursor.close()

    #Test getSpecific()
    connect()
    print(getSpecific({"Year": '2017', "Term": 3, "Type": 'LEC'}))
    cursor.close()










