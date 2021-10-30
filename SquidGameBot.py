#!/usr/bin/env python
# coding: utf-8

# # Squid Game Bot

# ## Introduction

# This bot simulates in Twitter some parts from the Squid Game series, without making spoilers, just tweeting and replying to mentions. It has been created to try the Twitter API in a funny way.
# The tweepy library has been used to make it easier to code.
# The bot has two operating phases:
# 
# 1. Recruiting: In this phase the bot registers in the game the Twitter users who tweet mentioning him and saying they want to participate. It also informs about how to get registered if the requirements haven't been satisfied. I have used tweepy.Stream to search for new tweets and reply them in real time.
# 
# 2. Game and eliminations: In this phase the bot informs that the game has started and tweets once an hour a new player that has been eliminated. Finally, when there is just one player left the game finishes and the winner is published. Here it is only used the update_status tweepy method.

# ## Code

# ### Setup

# In[ ]:


# Imports
import tweepy
import json
import random


# In[ ]:


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


# ### Phase 1: Recruiting

# In[ ]:


# Methods that will be executed by the stream
def load_image(name):
    """Loads an image from storage and returns the image id"""
    img = open(name, 'rb')
    return api.media_upload(filename="resources/card.jpg",file=img)

def check_status(status):
    """Checks if a status meets the requirements"""
    if 'particip' in status.text.lower():
        return True
    else:
        return False
        
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

def save_players(players):
    """Saves the players dictionary to file"""
    with open('resources/players.json', "w") as file:
        json.dump(players, file, indent=2)
        print('Players saved correctly')


# In[ ]:


# The tweepy Stream class is extended
class BotListener(tweepy.Stream):
    """This class implements the behaviour of the bot during the recruiting phase"""
    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret, players, id_imagen):
        super().__init__(consumer_key, consumer_secret, access_token, access_token_secret)
        self.players = players
        self.id_imagen = id_imagen
    
    def on_status(self, status):
        if check_status(status):
            if self.players.get(status.user.screen_name) is None:
                self.add_player(status)
            else:
                new_status = api.update_status('Lo siento, no puedes participar 2 veces', in_reply_to_status_id=status.id)
        else:
            new_status = api.update_status('Instrucciones de registro:\n'+
                                            '1) Etiquetarme en el tweet\n'+
                                            '2) Que el tweet contenga la palabra "participo"\n',
                                            in_reply_to_status_id=status.id)        

    def on_error(self, status_code):
        print('On error')
        print(status_code)
        if status_code == 420:
            save_players(self.players)
            return False
        else:
            save_players(self.players)
            return True
        
    def on_exception(self, exception):
        print('On exception')
        print(exception)
        if exception.apicode == 324:
            self.id_imagen = load_image("resources/card.jpg")
        
    def on_closed(self, response):
        save_players(self.players)
        print('On closed')
        print(response)
        
    def on_disconnect(self):
        save_players(self.players)
        print('On disconnect')
        print('Stream closed')

    def add_player(self, status):
        """Adds a new player to the dictionary and replies the tweet to confirm the registration"""
        num_player = len(self.players.keys()) + 1
        self.players[status.user.screen_name] = num_player
        status_response = api.update_status('Bienvenido al Juego @' + status.user.screen_name + '. Tu número es el '
                                           + str(num_player), in_reply_to_status_id=status.id, 
                                           media_ids=[self.id_imagen.media_id_string])
        print('Player ' + status.user.screen_name + ' added')


# In[ ]:


# A BotListener object is created
tweepy_stream = BotListener(consumer_key, consumer_secret, access_token, access_token_secret,
                            load_players(), load_image("resources/card.jpg"))

# And executed
thread = tweepy_stream.filter(track=['@SquidGameBotEs'], threaded=True)


# In[ ]:


# To stop the bot and close the stream
tweepy_stream.disconnect()


# In[ ]:


# To check if the stream is running or not
tweepy_stream.running


# ### Phase 2: Game and eliminations

# In[ ]:


# The players dictionary is loaded
players = load_players()


# In[ ]:


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


# ### Future

# If the bot succeed I would like to make this process more automatic and add different types of tweets to inform how a player has been eliminated.
