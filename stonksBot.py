import discord
from discord.ext import commands
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
import schedule
import time
import threading
import signal

#discord client global
client = commands.Bot(command_prefix = '.')

#gspread client global
scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client2 = gspread.authorize(creds)
sheet = client2.open("Stalking the Stalk Market").get_worksheet(1)

#global helper variables
running=True
connectedStartTime = datetime.datetime.now()
lowestUser = sheet.acell('N1').value

def reconnectGspread():
    global scope
    global creds
    global client2
    global sheet
    global connectedStartTime
    connectedStartTime = datetime.datetime.now()
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client2 = gspread.authorize(creds)
    sheet = client2.open("Stalking the Stalk Market").get_worksheet(1)

def clearDouble():
    global connectedStartTime
    if datetime.datetime.now() > connectedStartTime + datetime.timedelta(minutes=10):
        reconnectGspread()
    curList = sheet.col_values(17)
    curRow = 1
    for h in curList:
        sheet.update_cell(curRow,17,"")
        sheet.update_cell(curRow,16,"")
        curRow = curRow + 1

@client.event
async def on_ready():
    print('Ready!')

@client.event
async def on_message(message):
    username = message.author.name.split('#')[0]
    if not message.author.bot:
        if message.channel.name in ["animal-stonks","bot-spam"]:
            global connectedStartTime
            if datetime.datetime.now() > connectedStartTime + datetime.timedelta(minutes=10):
                reconnectGspread()
            # handle stonks
            # if sunday
            if datetime.datetime.today().weekday() == 6:
                global lowestUser
                ind = message.content.find(':stonks:')
                if ind > 1:
                    temp = ind-2
                    value = ''
                    while True:
                        if temp>=0:
                            if message.content[temp].isnumeric():
                                value = message.content[temp] + value
                                temp = temp - 1
                            else:
                                break
                        else:
                            break
                    if value != '':
                        curNum = int(sheet.acell('O1').value)
                        newNum = int(value)
                        if curNum < newNum:
                            await message.channel.send("Thanks for reporting {}, but {} got you beat with {}".format(username,lowestUser,curNum))
                        elif curNum == newNum:
                            await message.channel.send("Oh damn {}, your tied with {}, maybe help out with hosting unless someone reports lower".format(username,lowestUser,curNum))
                        else:
                            await message.channel.send("THIS IS NOT A DRILL!!!NEW LOW!!!!    ...    {}".format(newNum))
                            sheet.update_acell('O1',newNum)
                            sheet.update_acell('N1',message.author.name.split('#')[0])
                            lowestUser = username
                elif ind >=0:
                    await message.channel.send("You must be new here... its 'number:stonks:'")
            # if weekday
            else:
                ind = message.content.find(':stonks:')
                if ind > 1:
                    temp = ind-2
                    value = ''
                    while True:
                        if temp>=0:
                            if message.content[temp].isnumeric():
                                value = message.content[temp] + value
                                temp = temp - 1
                            else:
                                break
                        else:
                            break
                    if value != '':
                        r = random.randint(1,13)
                        if r == 1:
                            await message.channel.send('This is your broker, {} is reporting {} bells for turnips'.format(username,value))
                        elif r == 2:
                            await message.channel.send("Can't a bot get a break? Alright, {} is reporting {} bells for turnips I guess...".format(username,value))
                        elif r == 3:
                            await message.channel.send("Capitalist pig {} can sell turnips for {} bells".format(username,value))
                        elif r == 4:
                            await message.channel.send("JFC, I need to start charging interest. Ok, well, {} is reporting {} bells for turnips".format(username,value))
                        elif r == 5:
                            await message.channel.send("Tell me more {} about your {} bells priced turnips!".format(username,value))
                        elif r == 6:
                            await message.channel.send("{} reporting {} bells for turnips! A lovely stonk indeed!".format(username,value))
                        elif r == 7:
                            await message.channel.send("{} reporting {} bells for turnips! Big stonker! Big stonker!".format(username,value))
                        elif r == 8:
                            await message.channel.send("{} reporting {} bells for turnips! With stonks like these, who needs friends!".format(username,value))
                        elif r == 9:
                            await message.channel.send("{} reporting {} bells for turnips! Uh oh! Stonky!".format(username,value))
                        elif r == 10:
                            await message.channel.send("{} reporting {} bells for turnips! Big stonky! Big stonky!".format(username,value))
                        elif r == 11:
                            await message.channel.send("{} reporting {} bells for turnips! You can talk the talk, but can you stonk the stonk?".format(username,value))
                        elif r == 12:
                            await message.channel.send("{} reporting {} bells for turnips! Turnip for what?".format(username,value))
                        elif r == 13:
                            await message.channel.send("{} reporting {} bells for turnips! Welcome to the stalk markets motherfucker.".format(username,value))
                        curReportedList = sheet.col_values(1)
                        userRow = -1
                        if username in curReportedList:
                            userRow = curReportedList.index(username)+1
                        else:
                            if len(curReportedList) == 0:
                                userRow = 2
                            else:
                                userRow = len(curReportedList)+1
                            sheet.update_acell('A{}'.format(userRow),username)
                        dataCol = 2
                        dataCol = dataCol + datetime.datetime.today().weekday()*2 
                        timeModifier = 0
                        for role in message.author.roles:
                            if role.name == 'West Coast':
                                timeModifier = -3
                        if (int(datetime.datetime.now().hour)+timeModifier)%24>=12:
                            dataCol = dataCol + 1
                        sheet.update_cell(userRow,dataCol,int(value))
                    else:
                        await message.channel.send("You must be new here... its 'number:stonks:' ... no spaces!")
                elif ind>=0:
                    await message.channel.send("You must be new here... its 'number:stonks:'")

            # handle daily double
            ind = message.content.find(':dailydouble:')
            if ind > 1:
                temp = ind-2
                value = ''
                while True:
                    if temp>=0:
                        if message.content[temp]!='>':
                            value = message.content[temp] + value
                            temp = temp - 1
                        else:
                            break
                    else:
                        break
                if value != '':
                    r = random.randint(1,5)
                    if r == 1:
                        await message.channel.send('*Jeopardy Sirens*    What is    ...    {}'.format(value))
                    elif r == 2:
                        await message.channel.send("Hollup, you're saying    ....    {}    ...    is up for :dailydouble:!?".format(value))
                    elif r == 3:
                        await message.channel.send("Time to get rich off of    ....    {}".format(value))
                    elif r == 4:
                        await message.channel.send("Gee Bill! Mom let's you sell *two*    ....    {}".format(value))
                    elif r == 5:
                        await message.channel.send("Reporting your daily double    ....    {}".format(value))
                    curList = sheet.col_values(17)
                    curRow = len(curList)+1
                    sheet.update_acell('Q{}'.format(curRow),value)
                    sheet.update_acell('P{}'.format(curRow),username)

            # handle fossil offers
            ind = message.content.find(':skeletorKek:')
            if ind > 1:
                temp = ind-2
                value = ''
                while True:
                    if temp>=0:
                        if message.content[temp]!='>':
                            value = message.content[temp] + value
                            temp = temp - 1
                        else:
                            break
                    else:
                        break
                if value != '':
                    curList = sheet.col_values(17)
                    curRow = len(curList)+1
                    sheet.update_acell('Q{}'.format(curRow),value)
                    sheet.update_acell('P{}'.format(curRow),username)

def scheduleRunner():
    while True:
        global running
        if not running:
            break
        schedule.run_pending()
        time.sleep(3)
t1 = threading.Thread(target=scheduleRunner)

def keyboardInterruptHandler(signal,frame):
    global running
    running = False
    t1.join()
    exit(0)

## TODO print a set of helpful tips on syntax and hot to use the bot!
def printHelp():
    return None

## WIP: define the material cost of a piece of furniture
def addMaterials(inputString):
    costMap,costKeys = getMaterialCosts()

    # [amount, material] array
    cost = [materialCost.split(' ') for materialCost in inputString.split(',')]
    # attempt to sanitize input
    for costTuple in cost:
        amount, material = costTuple
        for costKey in costKeys:
            if material in costKey:
                costTuple = [amount,costKey]

    ## TODO: add a bit here that posts it on the google doc

    ## TODO: call calculateValue and update doc/post it in the disc

    return cost

## calculate the sell value of a piece of furniture given its material cost
def calculateValue(inputString):
    costMap,costKeys = getMaterialCosts()

    value = 0

    for materialCost in inputString.split(','):
        amount, material = materialCost.split(' ')

        if material in costKeys:
            value += costMap[material]*amount
        # catch shorthand errors (like 'iron' instead of 'iron nuggets')
        else:
            if any([material in costKey for costKey in costKeys]):
                for costKey in costKeys:
                    if material in costKey:
                        value += costMap[costKey]*amount

    return 2*value

## TODO: lookup everyone's fossil checklists and display
##          whether or not anyone needs a given fossil. 
def matchFossils():
    return None

## TODO: post a fossil for offer on the fossil exchange
def offerFossils():
    return None

## TODO: clear a user's offered fossils
def clearFossils():
    return None

## TODO: claim a fossil that is being offered. Removes it
##          from the offer list and adds it to their checklist
def claimFossil():
    return None

def getMaterialCosts():
    costMap = {'Tree branch':5,'Wood':60,'Softwood':60,'Hardwood':60,\
    'Stone':75,'Clay':100,'Iron nugget':375,'Gold nugget':10000,'Acorn':200,\
    'Pinecone':200,'Bamboo piece':80,'Young spring bamboo':200,'Bamboo shoot':250,\
    'Clump of weeds':10,'Cherry-blossom petal':None,'Fruit':100,'Fruit-foreign':500,\
    'Wasp nest':300,'Rusted part':10,'Boot':10,'Old tire':10,'Empty can':10,\
    'Star fragment':50,'Large star fragment':2500}
    costKeys = costMap.keys()

    return costMap, costKeys

signal.signal(signal.SIGINT, keyboardInterruptHandler)

schedule.every().day.at("22:00").do(clearDouble)
schedule.every().day.at("08:00").do(clearDouble)

t1.start()

with open('discordCred.txt.') as f:
    discord_key = f.read()
    client.run(discord_key)
