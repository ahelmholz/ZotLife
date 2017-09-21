import re
import requests
from collections import defaultdict




def getWebText(dept:str, year:str)->str:
    """Passes the parameters to the webpage and returns the text from the server"""
    print(dept, year)
    url = 'http://www.reg.uci.edu/perl/WebSoc'
    parameters = {
        'Submit': 'Display+Text+Results',
        'YearTerm': year,  # 2017-14
        'ShowComments': 'on',
        'ShowFinals': 'on',
        'Dept': dept,
        'Division': 'ANY',
        'ClassType:': 'ALL',
        'CancelledCourses': 'Exclude'
    }
    text = requests.post(url,data=parameters).text
    #remove extra info from beginning
    text = text.split("      _________________________________________________________________")[-1]
    #remove extra text from the end
    text = text.split("*** Total Classes Displayed:")[0]
    return text

def webTextToDict(text:str)->dict:
    """Takes the text from webreg and converts the class data into a dictionary"""
    #TODO: Rewrite and add comments as to how each part of this works. It is not grabbbing all the classes(Not even getting the title-->index)
    text = text.split('\n\n')
    masterDict = dict()
    for elClass in text:
        lineNum = -1
        index = str()
        for line in elClass.split('\n'):
            lineNum += 1
            if lineNum == 0:
                index = "_".join(line.split())
                if index != '':
                    masterDict[index] = list()
            elif lineNum != 1:
                value = re.search(
                    r"(\d{5})\s+([A-Z]{3})\s+([A-Z0-9]{1,2})\s+(\d{1,2})\s+([\w\s'\-]+,\s+\w+.|STAFF)\s+([\w\*]+)\s+([0-9:\-]+\s*[0-9:\-p]+|\s*)\s+(ON LINE|\w+\s\d+\w?|\*TBA\*)\s+(\w+,\s\w+\s\d+,\s\d+:\d+-\d+:\d+[ap]m|TBA|\s)\s+(\d+)\s+(\d+\/\d+|\d+)\s+(n\/a|)?(\s*\d+)\s*(\d+)?\s*([A-EG-N-P-Z&]+)?\s*(FULL|OPEN|Waitl)",
                    line
                )
                if value:
                    masterDict[index].append(value.groups())

    return masterDict


def getAllData()->dict:
    '''Grabs all the years, quarters, and departments data'''
    years = {
        #"2017  Fall Quarter":"2017-92",
        # "2017  Summer Session 2":"2017-76",
        # "2017  Summer Qtr (COM)":"2017-51",
        # "2017  10-wk Summer": "2017-39",
        # "2017  Summer Session 1": "2017-25",
         "2017  Spring Quarter": "2017-14",
        # "2017  Winter Quarter": "2017-03",
        # "2016  Fall Quarter": "2016-92",
        # "2016  Summer Session 2": "2016-76",
        # "2016  Summer Qtr (COM)": "2016-51 ",
        # "2016  10-wk Summer": "2016-39 ",
        # "2016  Summer Session 1": "2016-25",
        # "2016  Spring Quarter": "2016-14",
        # "2016  Winter Quarter": "2016-03",
        # "2015  Fall Quarter": "2015-92 ",
        # "2015  Summer Session 2": "2015-76 ",
        # "2015  Summer Qtr (COM)": "2015-51",
        # "2015  10-wk Summer": "2015-39",
        # "2015  Summer Session 1": "2015-25",
        # "2015  Spring Quarter": "2015-14",
        # "2015  Winter Quarter": "2015-03",
        # "2014  Fall Quarter": "2014-92",
        # "2014  Summer Session 2": "2014-76",
        # "2014  Summer Qtr (COM)": "2014-51",
        # "2014  10-wk Summer": "2014-39",
        # "2014  Summer Session 1": "2014-25",
        # "2014  Spring Quarter": "2014-14",
        # "2014  Winter Quarter": "2014-03",
        # "2013  Fall Quarter": "2013-92",
        # "2013  Summer Session 2": "2013-76",
        # "2013  Summer Qtr (COM)": "2013-51",
        # "2013  10-wk Summer": "2013-39",
        # "2013  Summer Session 1": "2013-25",
        # "2013  Spring Quarter": "2013-14 ",
        # "2013  Winter Quarter": "2013-03",
        # "2012  Fall Quarter": "2012-92",
        # "2012  Summer Session 2": "2012-76",
        # "2012  Summer Qtr (COM)": "2012-51",
        # "2012  10-wk Summer": "2012-39",
        # "2012  Summer Session 1": "2012-25 ",
        # "2012  Spring Quarter": "2012-14",
        # "2012  Winter Quarter":"2012-03"
    }
    departments = {
        "AC ENG": "AcademicEnglish and ESL",
        "AFAM": "African American Studies",
        "ANTHRO": "Anthropology",
        "ARABIC": "Arabic",
        "ART": "Art",
        "ART HIS": "Art History",
        "ARTS": "Arts",
        "ARTSHUM": "Arts and Humanities",
        "ASIANAM": "Asian American Studies",
        "BIO SCI": "Biological Sciences",
        "BME": "Biomedical Engineering",
        "CBEMS": "Chemical Engr and Materials Science",
        "CEM": "Community and Environmental Medicine",
        "CHC/LAT": "Chicano Latino",
        "CHEM": "Chemistry",
        "CHINESE": "Chinese",
        "CLASSIC": "Classics",
        "COGS": "Cognitive Sciences",
        "COM LIT": "Comparative Literature",
        "COMPSCI": "Computer Science",
        "CRM/LAW": "Criminology Law and Society",
        "CSE": "Computer Science and Engineering",
        "DANCE": "Dance",
        "DEV BIO": "Developmental and CellBiology",
        "DRAMA": "Drama",
        "E ASIAN": "East Asian Languages and Literatures",
        "EARTHSS": "Earth System Science",
        "ECON": "Economics",
        "EDUC": "Education",
        "EECS": "Electrical Engineering & Computer Science",
        "ENGLISH": "English",
        "ENGR": "Engineering",
        "ENGRCEE": "Engineering Civil and Environmental",
        "ENGRMAE": "Engineering Mechanical and Aerospace",
        "EPIDEM": "Epidemiology",
        "EURO ST": "European Studies",
        "FLM&MDA": "Film and Media Studies",
        "FRENCH": "French",
        "GEN&SEX": "Gender and Sexuality Studies",
        "GERMAN": "German",
        "GLBL ME": "Global Middle East Studies (started 2016 Fall)",
        "GLBLCLT": "Global Cultures",
        "GREEK": "Greek",
        "HEBREW": "Hebrew",
        "HINDI": "Hindi",
        "HISTORY": "History",
        "HUMAN": "Humanities",
        "HUMARTS": "Humanities and Arts",
        "I&C SCI": "Information and Computer Science",
        "IN4MATX": "Informatics",
        "INTL ST": "International Studies",
        "ITALIAN": "Italian",
        "JAPANSE": "Japanese",
        "KOREAN": "Korean",
        "LATIN": "Latin",
        "LINGUIS": "Linguistics",
        "LIT JRN": "Literary Journalism",
        "LPS": "Logic and Philosophy of Science",
        "MATH": "Mathematics",
        "MED": "Medicine",
        "MED HUM": "Medical Humanities",
        "MGMT": "Management",
        "MUSIC": "Music",
        "NUR SCI": "Nursing Science",
        "PERSIAN": "Persian",
        "PHILOS": "Philosophy",
        "PHRMSCI": "Pharmaceutical Sciences",
        "PHY SCI": "Physical Science",
        "PHYSICS": "Physics",
        "POL SCI": "Political Science",
        "PORTUG": "Portuguese",
        "PP&D": "Planning Policy and Design",
        "PSY BEH": "Psychology and Social Behavior",
        "PSYCH": "Psychology",
        "PUBHLTH": "Public Health",
        "REL STD": "Religious Studies",
        "ROTC": "Reserve Officers' Training Corps",
        "RUSSIAN": "Russian",
        "SOC SCI": "Social Science",
        "SOCECOL": "Social Ecology",
        "SOCIOL": "Sociology",
        "SPANISH": "Spanish",
        "SPPS": "Social Policy & Public Service",
        "STATS": "Statistics",
        "TAGALOG": "Tagalog",
        "TOX": "Toxicology",
        "UCDC": "Washington DC",
        "UNI AFF": "University Affairs",
        "UNI STU": "University Studies",
        "VIETMSE": "Vietnamese",
        "VIS STD": "Visual Studies",
        "WRITING": "Writing",
    }
    masterDict = defaultdict(list)
    for year in years:
        tempDict = dict()
        for dept in departments:
            text = getWebText(dept,years[year])
            data = webTextToDict(text)
            tempDict[dept] = data
            print("-->" + dept)
        masterDict[years[year]].append(tempDict)
        print("*" * 40)
        print(year)
        print("*"*40)

    return dict(masterDict)




















if __name__ == "__main__":
    data = getAllData()
    for yearQuarter in data:
        for dept in data[yearQuarter]:
            for value in dept.values():
                print("{}:\n\n\n\n\n{}".format(yearQuarter, value))