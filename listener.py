# -*- coding: utf-8 -*-
"""
Created on Tue Jun  9 23:20:39 2015

@author: nicholashamlin

"""
import json
import time
# import os #Only used during debugging process

from tweepy import StreamListener
import tweepy

from boto.s3.connection import S3Connection
from boto.s3.key import Key

class SListener(StreamListener):

    def __init__(self, api = None, prefix1 = 'streamer',prefix2='streamer2'):
        """Create log, counters, and output files for each type of tweet we care about"""
        self.api = api
        self.counter1 = 0
        self.counter2 = 0
        self.counter3 = 0
        self.prefix1 = prefix1
        self.prefix2 = prefix2
        self.output1  = open(prefix1 + '.'+time.strftime('%Y%m%d-%H%M%S') + '.json', 'w')
        self.output2  = open(prefix2 + '.'+ time.strftime('%Y%m%d-%H%M%S') + '.json', 'w')
        self.output3  = open('#both.' + time.strftime('%Y%m%d-%H%M%S') + '.json', 'w')
        self.log=open('log.txt','a')        
        self.output1.write("[")
        self.output2.write("[")
        self.output3.write("[")

    def on_data(self, data):

        if  'in_reply_to_status' in data:
            self.on_status(data)
        elif 'limit' in data:
            if self.on_limit(json.loads(data)['limit']['track']) is False:
                return False
        elif 'warning' in data:
            warning = json.loads(data)['warnings']
            self.log.write(warning['message'])
            return False

    def on_status(self, status):
        """
        This is the meat of the program that handles the classification of each tweet
        and chunks them into files based on hashtags.  I recognize that it would've
        been cleaner to split this into multiple functions, but I needed to get
        the program running prior to Game 6 in order to collect meaningful data.
        
        Consequently, inline comments only appear in the first IF statement, but 
        the same approach is used for each subsequent section.
        """
        if self.prefix1 in status and self.prefix2 in status:
            self.output3.write(unicode(status) + "\n]")
            self.counter3+=1
            msg=str(time.strftime('%Y%m%d-%H%M%S'))+" "+str(self.counter3)+ ' tweets for both'+'\n'
            print msg #Allows for tracking of tweets as they come in for debugging.  This data isn't stored
            self.output3,self.counter3=self.check_counter(self.counter3,self.output3,'#both',5000)
            
            # Write comma in JSON file if the Tweet isn't the first in a new file
            if self.counter3>0:
                self.output3.seek(0,2)
                size=self.output3.tell()
                self.output3.truncate(size-1)
                self.output3.write(",")

        elif self.prefix1 in status:
            self.output1.write(unicode(status) + "\n]")
            self.counter1+=1
            msg=str(time.strftime('%Y%m%d-%H%M%S'))+" "+str(self.counter1)+ ' tweets for '+self.prefix1+'\n'
            print msg            
            self.output1,self.counter1=self.check_counter(self.counter1,self.output1,self.prefix1,5000)
            
            if self.counter1>0:
                self.output1.seek(0,2)
                size=self.output1.tell()
                self.output1.truncate(size-1)
                self.output1.write(",")
                
        elif self.prefix2 in status:
            self.output2.write(unicode(status) + "\n]")
            self.counter2+=1
            msg=str(time.strftime('%Y%m%d-%H%M%S'))+" "+str(self.counter2)+ ' tweets for '+self.prefix2+'\n'
            print msg            
            self.output2,self.counter2=self.check_counter(self.counter2,self.output2,self.prefix2,5000)
            
            if self.counter2>0:
                self.output2.seek(0,2)
                size=self.output2.tell()
                self.output2.truncate(size-1)
                self.output2.write(",")
        return
    
    def write_to_s3 (self,file):
        """ Given a file, upload it to S3 bucket specified below"""
        myKey.key = file.name
        try:
            myKey.set_contents_from_filename(file.name)
        except Exception as e:
            self.log.write(str(time.strftime('%Y%m%d-%H%M%S'))+str(e)+'\n')
        return      

    def check_counter(self,counter,output,prefix,threshold):
        """ Evaluate if an active file has reached a threshold of tweets.  If so,
        close the chunk, upload it to S3, and open a new one"""
        
        if counter>=threshold:
            #truncate trailing comma to maintain JSON format
            output.seek(0,2)
            size=output.tell()
            output.truncate(size-2)
            output.write("]")
            output.close()
            self.write_to_s3(output)
            output=open(prefix + '.'+ str(time.strftime('%Y%m%d-%H%M%S')) + '.json', 'w')
            counter=0
            self.log.write(str(time.strftime('%Y%m%d-%H%M%S'))+' reset file for '+prefix)
        return output,counter

    def on_limit(self, track):
        """ Record rate limiting events to log file"""
        self.log.write(str(time.strftime('%Y%m%d-%H%M%S'))+str(track) + "\n")
        return

    def on_error(self, status_code):
        """ Record misc. twitter errors and corresponding status codes to log file"""
        self.log.write(str(time.strftime('%Y%m%d-%H%M%S'))+' Error: ' + str(status_code) + "\n")
        return False

    def on_timeout(self):
        """ If timeout occurs, note event in log file and pause before continuing"""
        self.log.write(str(time.strftime('%Y%m%d-%H%M%S'))+" Timeout, sleeping for 60 seconds...\n")
        time.sleep(60)
        return
        
    def on_disconnect(self):
        """ If connection is lost, note event in log file and pause before continuing"""
        self.log.write(str(time.strftime('%Y%m%d-%H%M%S'))+" Disconnected, sleeping for 60 seconds...\n")
        time.sleep(60)        
        return

# Twitter API Authentication and Connection
consumer_key = "<CONSUMER KEY>";
consumer_secret = "<CONSUMER SECRET>";
access_token = "<ACCESS TOKEN>";
access_token_secret = "<ACCESS TOKEN SECRET>";
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

# AWS Authentication and Connection
conn = S3Connection('<AWS_ACCESS_KEY>', '<AWS_SECRET_KEY>')
myBucket = conn.get_bucket('hamlin-mids-assignment2')
myKey = Key(myBucket)


if __name__ == '__main__':
    
## The following code was used during debugging to clear out old files from
## past attempts.  It's not used in the final implementation, but was useful
## during its creation.
#    
#    for fname in os.listdir(os.getcwd()):
#        if fname.startswith("#"):
#            os.remove(fname)   

    track = ['#Warriors', '#NBAFinals2015']
    listen = SListener(api, '#Warriors', '#NBAFinals2015')
    stream = tweepy.Stream(auth, listen)

    print "Streaming started..."
    #This loop ensures that in the event of an error, the problem is logged and
    #data is secured before reconnecting and restarting the connection process.
    while True:
        try: 
            stream.filter(track = track)
            
        except Exception as e:
            # if an error occurs, record event in log file, write all
            # active chunks and log file to s3 for safety.
            msg=str(time.strftime('%Y%m%d-%H%M%S'))+'-'+str(e)
            listen.log.write(msg)
            print msg
            listen.output1.write(']')
            listen.output2.write(']')
            listen.output3.write(']')
            stream.disconnect()
            listen.write_to_s3(listen.output1)
            listen.write_to_s3(listen.output2)
            listen.write_to_s3(listen.output3)
            listen.write_to_s3(listen.log)
        
        #Manually stop everything.  The program will run until you turn it off.
        except (KeyboardInterrupt, SystemExit):
            listen.log.close()
            listen.write_to_s3(listen.output1)
            listen.write_to_s3(listen.output2)
            listen.write_to_s3(listen.output3)
            listen.write_to_s3(listen.log)
            print "Stopping Stream..."
            stream.disconnect()
            break
        
