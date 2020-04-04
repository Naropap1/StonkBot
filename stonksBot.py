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
misc_sheet = client2.open('Stalking the Stalk Market').worksheet('Misc')
usermap = {username: realname for realname,username in zip(misc_sheet.col_values(6)[1:],misc_sheet.col_values(7)[1:])}
sheet = client2.open('Stalking the Stalk Market').worksheet('Data')

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
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client2 = gspread.authorize(creds)
    sheet = client2.open('Stalking the Stalk Market').worksheet('Data')

def clearDouble():
    global connectedStartTime
    if datetime.datetime.now() > connectedStartTime + datetime.timedelta(minutes=10):
        reconnectGspread()
    curList = sheet.col_values(17)
    curRow = 1
    for h in curList:
        sheet.update_cell(curRow,17,"")
        sheet.update_cell(curRow,18,"")
        sheet.update_cell(curRow,19,"")
        #sheet.update_cell(curRow,16,"")
        curRow = curRow + 1

@client.event
async def on_ready():
    print('Ready!')

@client.event
async def on_message(message):
    global usermap
    if not message.author.bot:
        if message.channel.name in ["animal-stonks","bot-spam"]:
            global connectedStartTime
            if datetime.datetime.now() > connectedStartTime + datetime.timedelta(minutes=10):
                reconnectGspread()

            username = message.author.name.split('#')[0]
            userList = sheet.col_values(16)
            if username in usermap:
                username = usermap[username]
                user_idx = userList.index(username)
            else:
                user_idx = len(userList)+1

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
                        if value == 'HELP':
                            await message.channel.send(getHelpText())
                        else:
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
            # if not sunday
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
                            if role.name in ['West Coast','PDT','PST','WC','PST/PDT','PDT/PST']:
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

                    lookup_res = lookupItem(value)
                    if lookup_res:
                        value = lookup_res[0]
                        item_cost = lookup_res[1].replace(',','')
                        if item_cost.isnumeric():
                            item_cost = '{:,}'.format(2*int(item_cost))
                        else:
                            item_cost = '???'
                        item_mats = lookup_res[2]
                        value_string = '({} Bells <:isabelleDab:692772908166021150> {})'.format(item_cost, item_mats)
                        if lookup_res[3].isnumeric():
                            item_ratio = float(lookup_res[3])
                        else:
                            item_ratio = 1.00
                    else:
                        item_cost = ''
                        item_mats = ''
                        value_string = ''
                        item_ratio = 1.00

                    r = random.randint(1,5)
                    if r == 1:
                        await message.channel.send('*Jeopardy Sirens*    What is    ...    {} {}'.format(value,value_string))
                    elif r == 2:
                        await message.channel.send("Hollup, you're saying    ....    {}    ...    is up for <:dailydouble:692011979274977301>!? {}".format(value,value_string))
                    elif r == 3:
                        await message.channel.send("Time to get rich off of    ....    {} {}".format(value,value_string))
                    elif r == 4:
                        await message.channel.send("Gee Bill! Mom let's you sell *two*    ....    {} {}".format(value,value_string))
                    elif r == 5:
                        await message.channel.send("Reporting your <:dailydouble:692011979274977301> daily double <:dailydouble:692011979274977301>    ....    {} {}".format(value,value_string))

                    if item_ratio <= 0:
                        await message.channel.send("*Careful*! This sells for less than it's materials! ({.2})".format(item_ratio))
                    elif item_ratio < 1:
                        await message.channel.send("Alas, this only sells for {.2} efficiency...".format(item_ratio))
                    elif item_ratio > 1:
                        await message.channel.send("<:naroPog:466231362563604492> This sells for {.2} profit over its materials!".format(item_ratio))

                    curRow = user_idx+1
                    sheet.update_acell('P{}'.format(curRow),username)
                    sheet.update_acell('Q{}'.format(curRow),value)
                    sheet.update_acell('R{}'.format(curRow),item_cost)
                    sheet.update_acell('S{}'.format(curRow),item_mats)

            # handle fossil offers
            ind = message.content.find(':skeletor:')
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
                    if value == 'CLEAR':
                        curRow = user_idx+1
                        sheet.update_acell('P{}'.format(curRow),username)
                        sheet.update_acell('T{}'.format(curRow),'')
                    else:  
                        r = random.randint(1,5)
                        if r == 1:
                            await message.channel.send('<:skeletor:689503610509328468> Them\'s some craaaaazy bones    ...    {}'.format(value))
                        elif r == 2:
                            await message.channel.send("Prospector {} is offering    ....    {} <:skeletor:689503610509328468>".format(username,value))
                        elif r == 3:
                            await message.channel.send("<:skeletor:689503610509328468> Dino dupe! <:skeletor:689503610509328468>    ....    {}".format(value))
                        elif r == 4:
                            await message.channel.send("Dang, {} needs a new shovel!    ....    {}".format(username,value))
                        elif r == 5:
                            await message.channel.send("Gotta dig 'em all! FossilDex exchange offer:    ....    {}".format(value))

                        curRow = user_idx+1
                        sheet.update_acell('P{}'.format(curRow),username)
                        sheet.update_acell('T{}'.format(curRow),value)

                        matches = matchFossils(value.split(','))
                        for match_row in matches:
                            if len(match_row[1]) >= 1:
                                r = random.randint(1,5)
                                if r == 1:
                                    await message.channel.send("<:skeletor:689503610509328468> We've got a match! {}: {}".format(match_row[0],', '.join(match_row[1])))
                                elif r == 2:
                                    await message.channel.send("<:skeletor:689503610509328468> We've got a match! {} needs a(n) {}".format(match_row[0],' and '.join(match_row[1])))
                                elif r == 3:
                                    await message.channel.send("<:skeletor:689503610509328468> We've got a match! {} could use a(n) {}".format(match_row[0],' or '.join(match_row[1])))
                                elif r == 4:
                                    await message.channel.send("<:skeletor:689503610509328468> We've got a match! {}'s Museum is lacking a(n) ' {}".format(match_row[0],' and '.join(match_row[1])))
                                elif r == 5:
                                    await message.channel.send("<:skeletor:689503610509328468> We've got a match! {} doesn't have a(n) {} yet. Throw 'em a bone!".format(match_row[0],' or '.join(match_row[1])))


def scheduleRunner():
    while True:
        global running
        if not running:
            break
        schedule.run_pending()
        time.sleep(3)
t1 = threading.Thread(target=scheduleRunner)

def keyboardInterruptHandler(signal,frame):
    print('Stopping...')
    global running
    running = False
    t1.join()
    exit(0)

## return a set of helpful tips on syntax and how to use the bot!
def getHelpText():
    help_txt = '''Hi, I'm StonksBot! There are currently *3* ways I can help you:
        1) <number><:stonks:692774931213189121>
            Update your current stalk market price. Cleared every Saturday 10PM.
            Make sure you are flaired properly if not in EST!
        2) <furniture><:dailydouble:692011979274977301>
            Update your current Hot item at the store. Cleared daily at 10PM.
            Note: Not all items have full price and material data yet! Fruit furniture pricing assumes foreign fruit.
        3) <fossils><:skeletor:689503610509328468>
            Update your currently offered fossils! Add them as a comma-separated list.
            Clear your current offers with CLEAR<:skeletor:689503610509328468>.
            Make sure you spell the names correctly, as they appear in your inventory!'''
    return help_txt

# cleans a string for item material/value lookup matching
def sanitizeString(inputString):
    punctuation = ['-',':','_','+',',','.',';','\'','\"','\\','/','|','<','>','(',')',\
                   '[',']','{','}','#','$','%','@','!','?','`','*','&','^']

    newString = inputString.strip(' \n\t')
    if newString[-3:] == 'x10':
        newString = newString[:-3]
    else:
        newString = newString
    for punct in punctuation:
        newString = newString.replace(punct,' ')
    newString = newString.strip(' \n\t')
    newString = newString.replace('-',' ')
    newString = newString.lower()

    return newString

# references the below spreadsheet to get material cost and sell value of DIY furniture items
def lookupItem(item_name):
    ref_sheet_URL = 'https://docs.google.com/spreadsheets/d/14_0mnSZSwIaBfjd_2MZvzeaymdxqYnkHlIS4iKA3NBk/edit?usp=sharing'
    item_name_clean = sanitizeString(item_name)

    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client2 = gspread.authorize(creds)
    val_sheet = client2.open_by_key('14_0mnSZSwIaBfjd_2MZvzeaymdxqYnkHlIS4iKA3NBk').worksheet('DIY Catalog')

    sheet_clean_names = [sanitizeString(sheet_name) for sheet_name in val_sheet.col_values(1)[2:]]
    if item_name_clean in sheet_clean_names:
        item_idx = sheet_clean_names.index(item_name_clean)
        row_vals = val_sheet.row_values(item_idx+3)

        item_name = row_vals[0]
        item_ratio = row_vals[1]
        item_value = row_vals[3]
        material_names = [mat_name for mat_name in val_sheet.row_values(1)[4:]]
        material_strings = [' '.join(duo) for duo in zip(row_vals[4:],material_names) if duo[0] != '' if int(duo[0])>0]
        item_materials = ', '.join(material_strings)
    else:
        return False

    return (item_name,item_value,item_materials,item_ratio)

## TODO: lookup everyone's fossil checklists and display
##          whether or not anyone needs a given fossil. 
def matchFossils(fossilList):
    f_sheet = client2.open('Stalking the Stalk Market').worksheet('Fossil Stock')
    names = f_sheet.col_values(1)[2:]

    titles = f_sheet.row_values(1)[1:]
    dinos = []
    last = ''
    for dino in titles:
        if dino in ['-','',' ']:
            dino = last
        last = dino
        dinos.append(last)

    parts = f_sheet.row_values(2)[1:]
    fossil_names = []
    for dino,part in zip(dinos,parts):
        if part in ['-','--','',' ']:
            f_part = dino
        elif part in ['Left Wing','Right Wing']:
            f_part = part[:-4]
            f_part = f_part + dino + ' Wing'
        else:
            f_part = dino +' '+ part
        fossil_names.append(f_part)
    fossil_names_clean = [sanitizeString(f_name) for f_name in fossil_names]

    matches = []

    for i in range(1,len(names)+1):
        username = names[i-1]
        user_bools = [True if val == 'TRUE' else False for val in f_sheet.row_values(2+i)[1:]]
        user_matches = []

        for fossil in fossilList:
            fossil_clean = sanitizeString(fossil)
            if fossil_clean in fossil_names_clean:
                f_idx = fossil_names_clean.index(fossil_clean)
                if not user_bools[f_idx]:
                    user_matches.append(fossil_names[f_idx])

        matches.append(user_matches)
    return [[name,match] for name,match in zip(names,matches)]

## TODO: claim a fossil that is being offered. Removes it
##          from the offer list and adds it to their checklist
def claimFossil():
    return None

def getMaterialCosts():
    cost_map = {'Tree branch':5,'Wood':60,'Softwood':60,'Hardwood':60,\
    'Stone':75,'Clay':100,'Iron nugget':375,'Gold nugget':10000,'Acorn':200,\
    'Pinecone':200,'Bamboo piece':80,'Young spring bamboo':200,'Bamboo shoot':250,\
    'Clump of weeds':10,'Cherry-blossom petal':None,'Fruit':100,'Fruit-foreign':500,\
    'Wasp nest':300,'Rusted part':10,'Boot':10,'Old tire':10,'Empty can':10,\
    'Star fragment':50,'Large star fragment':2500}
    cost_keys = cost_map.keys()

    return cost_map, cost_keys

signal.signal(signal.SIGINT, keyboardInterruptHandler)

schedule.every().day.at("22:00").do(clearDouble)
schedule.every().day.at("08:00").do(clearDouble)

t1.start()

with open('discordCred.txt.') as f:
    discord_key = f.read()
    client.run(discord_key)
