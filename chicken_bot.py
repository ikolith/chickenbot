import os
import discord
import random
#import sqlite3
import asyncio
import re
#import time for timer for chicken game

from io import BytesIO
from PIL import Image
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('BOT_TOKEN')
client = discord.Client()
#connection =  sqlite3.connect('chicken_game_data.db')
#crsr = connection.cursor()

@client.event
async def on_ready():
    print(f'{client.user} ready.')
    
    await client.change_presence(activity = discord.Game('Not yet !playing'))

@client.event
async def on_message(message):
    '''
    async def random_resize(message, fp, name='resize'):

        pic = Image.open(fp)#'.\\yud.jpeg'
        print(fp)
        pic = pic.resize((round(pic.size[0] * random.uniform(0.01,2)),round(pic.size[1] * random.uniform(0.01,2))))
        temp = BytesIO()
        print(pic.format)
        pic.save(temp, format='png')
        temp.seek(0)
        await message.channel.send(file=discord.File(temp, filename = name + '.' + pic.format))
    '''  
    if message.author == client.user:
        return
    '''
    if 'ur mom' in message.content.lower():
        await random_resize(message,'.\\crycat.png','crycat')
    '''
    if 'yud' in message.content.lower():
        
        yud = Image.open('.\\yud.jpeg')
        yud = yud.resize((round(yud.size[0] * random.uniform(0.01,2)),
        round(yud.size[1] * random.uniform(0.01,2))))
        temp = BytesIO()
        yud.save(temp, format='jpeg')
        temp.seek(0)
        await message.channel.send(file=discord.File(temp,filename='yud.jpeg'))

    if message.content.lower().startswith('!tobrazil'):
        await message.channel.send(':flag_br:' + '\n'*3 + 
        ' '*6 + '{}'.format(message.content[10:] + '\n'*4 + 
        ' '*16 + ':man_golfing:'))

    if message.content.lower().startswith('!playing '):
        await client.change_presence(activity = discord.Game(message.content[9:]))

    if message.content.lower().startswith('!playchicken'):
        game_channel = message.channel
        scoring_dict = {1:1, 2:3, 3:5, 4:7, 5:10, 6:13, 7:16, 8:19, 9:22, 10:30}
        point_ranking = {0:'', 20:'Tin', 50:'Copper', 100:'Bronze', 175:'Silver', 250:'Gold', 350:'Platinum', 500:'Diamond'}
        chicken_rules = (
                'Welcome to Chicken, a game for settling scores, squashing beefs, pestering your friends, and reaching the top of the pecking order.\n'+
                '----RULES----\n'+
                ' @ Another player to challenge them to a game of chicken. The game starts once they "!accept" the challenge.'+
                ' The player challenged gets 5 minutes to accept the challenge. After that each player gets a minute for their turn.\n'+
                ' If a player runs out of time they automatically chicken out.\n'+
                ' A random secret number of available steps between 5 and 100 will be chosen with a uniform distribution.\n'+
                ' Each player can take up to 10 steps at a time.\n'+
                ' The players are moving towards each other, so they share available steps.\n'+
                ' If the players take more steps than is available, the one that goes over loses... better rules incoming when I write more code involving records and current rank.\n'+
                ' If one player says "!chicken" they can back off and both players keep their points. The other player gets a win.\n'+
                ' Players can take steps by saying "!step #", for example "!step 7".\n'+
                '----SCORING----\n'+
                ' Taking more steps at a time is rewarded with more points as shown in this dictionary where "step:points".\n'+
                str(scoring_dict)+'\n'+
                '----POINT RANKING SYSTEM----\n'+
                'I didnt actually do this yet so just uh... try and win with as many points as possible? I dont know dude.\n'+
                str(point_ranking)+'\n'+
                '----PECKING ORDER----\n'
                'not there yet'
                '')
        #I would call these two "challenger" and "challengee" but reading those two over and over gets tiring as they differ by one letter
        #So they are "sender" of challenge and "receiver" of challenge
        
        sender = message.author
        sender_name = str(message.author)
        if len(message.mentions) == 1:
            pass
        else:
            message.mentions.clear()
            message.mentions.append(sender)       

        if message.content.lower().endswith('rules'):
            #current pecking order is based on wins stored in the db
            await game_channel.send(chicken_rules)
                #check if one other non bot player was mentioned who is not the same person as the author
        if (message.mentions[0].bot == False) and not (sender_name == str(message.mentions[0])):
            receiver_name = str(message.mentions[0])
            game_channel = message.channel
            await game_channel.send('Waiting for {} to !accept the challenge.'.format(receiver_name))
        
            def check_accepted(message):
                checked_message_sender_name = str(message.author)
                print(checked_message_sender_name)
                return message.content == '!accept' and message.channel == game_channel \
                    and checked_message_sender_name == receiver_name \
                    and not checked_message_sender_name == sender_name 

            try:
                msg = await client.wait_for('message', check=check_accepted, timeout=300.0)
            except asyncio.TimeoutError:
                await game_channel.send('{} took too long to accept the challenge.'.format(receiver_name))
            else:
                async def chicken_game(p1, p2):
                    p1_turn = True
                    p1_points = 0
                    p2_points = 0
                    steps_taken = 0
                    available_steps = random.randint(5,100)
                    def turn_checker(message):

                        step = re.findall( r'[1]?[\d]', message.content)

                        #step_int = int(''.join(step))

                        return ((str(message.author) == p1 and p1_turn == True) or (str(message.author) == p2 and p1_turn == False)) and \
                        ((message.content.startswith('!step') and len(step) == 1 and (int(''.join(step)) > 0 and int(''.join(step)) < 11)) or \
                        (message.content.startswith('!chicken')))
                        
                    #this triggers once, make it a while loop
                    while available_steps > 0:
                        print(available_steps)
                        if p1_turn:
                            await game_channel.send("It's {}'s turn! \"!step #\" where # is 0-10 to step".format(str(sender_name)))
                            
                        else:
                            await game_channel.send("It's {}'s turn! \"!step #\" where # is 0-10 to step".format(str(receiver_name)))
                            
                        try:
                            turn_message = await client.wait_for('message',check=turn_checker, timeout = 60.0)

                        except asyncio.TimeoutError:
                            await game_channel.send('Player took too long.') #and end the game
                        else: 
                            #i should define this elsewhere..? probably?
                            async def step_or_chicken(message):
                                if message.content.startswith('!step'):
                                    step_size = int(''.join(re.findall( r'[1]?[\d]', message.content)))
                                    print(step_size)
                                    return step_size
                                elif message.content.startswith('!chicken'):
                                    return 0
                                else:
                                    await game_channel.send('something is terrible broken')

                            step_size  = await step_or_chicken(turn_message)
                        
                        if step_size > 0: 
                            #game continues
                            available_steps = available_steps - step_size
                            print(available_steps)

                            if p1_turn:
                                p1_points += scoring_dict[step_size]
                                await game_channel.send('{} gains {} points!'.format(p1,scoring_dict[step_size]))
                            else:
                                p2_points += scoring_dict[step_size]
                                await game_channel.send('{} gains {} points!'.format(p2,scoring_dict[step_size]))

                            steps_taken += step_size
                            await game_channel.send('{} steps taken.'.format(steps_taken))

                            p1_turn = not p1_turn
                        
                        else:
                            if p1_turn:
                                #make this mean something
                                await game_channel.send('{} wins!\nThere were {} steps left.'.format(p2, available_steps))
                                available_steps = 0
                            else:
                                await game_channel.send('{} wins!\nThere were {} steps left.'.format(p1, available_steps))
                                available_steps = 0

                
                await chicken_game(sender_name,receiver_name)
        else:
            await message.channel.send('To play chicken you must @ one other user in the server who is not a bot.')

    if '!help' in message.content.lower():
        await message.channel.send('''"yud" Generates a yud of random size (not case sensitive).\n'''+
        '''"!playing" Lets you change what the bot is currently "Playing".\n'''+
        '''"!tobrazil" Sends things to brazil.''')

client.run(token)