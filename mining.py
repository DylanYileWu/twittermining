from __future__ import division
from datetime import datetime
import pytz
import tzlocal
import json
import pandas as pd
import re
import sys

class mining():
    # this function will read the given file that contains all the tweets
    def read_Twt_file(self, twt_file_path):
        twtdata=[]
        twt_file=open(twt_file_path,'r')
        for line in twt_file:
            try:
                tweet = json.loads(line)
                if tweet['text'] is None:continue
                twtdata.append(tweet)
            except:
                continue
        return twtdata

    # function returns True if any word in the wordlist that exists in the given text
    def tag_tweet(self, wordlist, text):
        text = text.lower()
        match=None
        # go through the revelant wordl list and check if any of the relvant word apears in the list
        for relevant_word in wordlist:
            relevant_word = relevant_word.lower()
            match = re.search(relevant_word, text)
            if match:break
        if match:
            return True
        return False

    # this function will open a file and collect all the words, then return a list object that contains all the words
    def word_list(self,filepath):
        returnlist=[]
        with open(filepath,'r') as f:
            for word in f:
                word=word.strip()
                returnlist.append(word)
        return returnlist

    # this function convert given time (UTC) to your local time
    def convert_tz(self,orginTime):
        local_timezone = tzlocal.get_localzone()
        time = datetime.strptime(orginTime, '%a %b %d %H:%M:%S +0000 %Y')
        local_time = time.replace(tzinfo=pytz.utc).astimezone(local_timezone)
        return local_time

    # this function changes the format of datetime
    def timeformat(self,time):
        return time.strftime("%Y-%m-%d %H:%M:%S")

def mainfunction(filepath,relvantwordfile,classfiledict):
    print 'Reading files'
    i=mining()
    twtdate= i.read_Twt_file(filepath)
    tweets = pd.DataFrame()

    print "Start Mining"
    # extrate texts from the tweet data (twtdate)
    tweets['text']=map(lambda  tweet:tweet['text'],twtdate)
    tweets['time']=map(lambda  tweet:tweet['created_at'],twtdate)

    #making all the word list
    #make the word list for releant word
    relevantList=i.word_list(relvantwordfile)

    # Convert time zoom
    # all the time from twitter API are UTF time zone
    # get it convert it your computer time zoom
    tweets['curtz'] = tweets['time'].apply(lambda tweet:i.convert_tz(tweet))

    # get all the user input classes and the associated file path
    classdict = dict(map(lambda (k,v): (k, i.word_list(v)), classfiledict.iteritems()))

    print "Finding your interested tweets"
    # tag all the relevant tweets according to relevantList (made by relvantwordfile)
    tweets['relevant'] = tweets['text'].apply(lambda tweet:i.tag_tweet(relevantList, tweet))

    #in case there is no relevant data
    if True not in tweets['relevant'].value_counts():
        sys.exit("No relevant data have been found, please collect more data or revise your keywords file")

    # tag all the wanted classes
    for targetClass,targetwordlist in classdict.iteritems():
        tweets[targetClass] = tweets['text'].apply(lambda tweet: i.tag_tweet(targetwordlist, tweet))

    # do some simple stats
    # total rows in the file
    # total relevant rows in the file
    # percentage of the wanted classes
    # show the result
    totalrows = len(tweets.index)
    totalRelCt= tweets['relevant'].value_counts()[True]
    print '+--------------+--------------+--------------+'
    print "|%10s    |%10s    |%10s    |"%("Classes","Counts","Percentage")
    for targetClass in classdict.keys():
        print '+--------------+--------------+--------------+'
        # in case the relevant twitter cannot be classified to a class
        # otherwise tweets[tweets['relevant'] == True][targetClass].value_counts()[True] will cause error
        if True not in tweets[tweets['relevant'] == True][targetClass].value_counts():
            classcount=0
        else:
            classcount = tweets[tweets['relevant'] == True][targetClass].value_counts()[True]
        row = "|%10s    |" % targetClass
        row += " %10i   |" % classcount
        row += " %10.2" \
               "%% |" %(classcount/totalRelCt*100)
        print row
    print '+--------------+--------------+--------------+'
    print '%i tweets are found in this file, %i ( %.2f %% of total) are relevant to what you want to discover'\
          %(totalrows,totalRelCt,totalRelCt/totalrows*100)
    print 'All the class(es) are counted based on %i relevant tweets '%(totalRelCt)
    print "These tweets are collected in time zone ''%s'' from : %s to %s" %(tweets['curtz'].iloc[0].tzname(),
            i.timeformat(tweets['curtz'].iloc[0]),i.timeformat(tweets['curtz'].iloc[-1]))

if __name__ == '__main__':
    # input example
    #python call function formati
    #mainfunction('./tweets-03','./relevant.txt',{'positive':'./positive.txt','negative':'./negative.txt'})
    # the following is for command line
    # the formation python mining.py tweetfile relevantfile class1=class1file class2=class2file
    # assuming all the file in the same directory
    # example: python mining.py ./tweets.txt ./relevant.txt positive=./positive.txt negative=./negative.txt
    f1=sys.argv[1]
    f2=sys.argv[2]
    restclassfiles = dict([arg.split('=', 1) for arg in sys.argv[3:]])
    mainfunction(f1,f2,restclassfiles)


