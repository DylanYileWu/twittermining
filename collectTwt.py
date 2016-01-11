#Import the necessary methods from tweepy library
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import sys

#Variables that contains the user credentials to access Twitter API
access_token = "####################################“
access_token_secret = "####################################“
consumer_key = "####################################“
consumer_secret = "####################################“


#This is a basic listener that just prints received tweets to stdout.
class StdOutListener(StreamListener):
    def __init__(self):
        self.outfiledir=""

    def on_data(self, data):
        with open(self.outfiledir,"a") as fid:
            fid.write(data+"\n")
        return True

    def on_error(self, status):
        print status


def mainfunction(outfilepath,tracklist):
    #This handles Twitter authetification and the connection to Twitter Streaming API
    l = StdOutListener()
    l.outfiledir=outfilepath
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = Stream(auth, l)

    #This line filter Twitter Streams to capture data by the keywords
    stream.filter(track=tracklist)

if __name__ == '__main__':
    # mainfunction( "./test2.txt",['stock', 'dow', 's&p 500'])
    # if you use command line, example of using this stript: python collectTwt.py outfilepath trackitem1 trackitem2.....
    f1=sys.argv[1]
    tracklist=sys.argv[2:]
    mainfunction(f1,tracklist)