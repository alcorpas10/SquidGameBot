# Imports
import tweepy
import json

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
        
# A BotListener object is created
tweepy_stream = BotListener(consumer_key, consumer_secret, access_token, access_token_secret,
                            load_players(), load_image("resources/card.jpg"))

# And executed
thread = tweepy_stream.filter(track=['@SquidGameBotEs'], threaded=True)