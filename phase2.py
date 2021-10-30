# Imports
import tweepy
import json
import random
import time

# Keys of the twitter application and user
consumer_key = "XXXXXXXXXXXXXXXXXXXXXXXXX"
consumer_secret = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

access_token = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
access_token_secret = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

# The access to the API is configured
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
 
# The connection with the API is established
api = tweepy.API(auth)

# Methods that will be executed by the stream
def load_image(name):
    """Loads an image from storage and returns the image id"""
    img = open(name, 'rb')
    return api.media_upload(filename="resources/card.jpg",file=img)
        
def load_players():
    """Loads the players dictionary from file"""
    try:
        with open('resources/players.json') as file:
            players = json.load(file)
            print('Players loaded correctly')
            return players
    except:
        print('Players created correctly')
        return {}

# The players dictionary is loaded
players = load_players()

# To keep the initial number of players
num_players = len(players)

# Initial tweet, from this moment, each hour, the bot tweets a new eliminated player
statusInit = api.update_status('¡¡¡Comienza el juego!!!\nA partir de ahora se eliminará un jugador cada hora hasta que '+ 
                               'solo quede uno.\nSuerte. 🔵🔺⬛')
time.sleep(3600)
while len(players) > 1:
    random_key = random.choice(players.keys())
    status = api.update_status('El jugador número '+players[random_key]+', @'+random_key+', ha sido eliminado\n'+
                              +'Quedan '+len(players.keys())+' jugadores de '+num_players)
    players.pop(random_key)
    time.sleep(3600)
    
# When there is only one player left the game finishes and the bot tweets who is the winner
winner = players.items()[0]
statusEnd = api.update_status('¡¡¡Fin del juego!!!\nEl ganador de esta edición de los juegos es el número ' + winner[1] + 
                               ', @' + winner[0], media_ids=load_image('resources/winner.jpg'))