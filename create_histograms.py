# -*- coding: utf-8 -*-
"""
Created on Wed Jun 10 00:42:54 2015

@author: nicholashamlin
"""
import os

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk import FreqDist

#Define both default and Twitter-specific stopwords for exclusion 
default_stops = (stopwords.words("english"))
custom_stops=['rt','ht','mt','@','#','!',':',';',',','.',"'s","?","\\n",'http','https',"n't","&","\\",'...','-','"']
stops=list(set(default_stops+custom_stops))

# Processing function also accepts another list of stopwords for call-specific exclusions
def process_tweets (hashtag,addl_stops=[]):
    count=0
    good_count=0
    words_to_plot=[]
    #Iterate through all chunked files with relevant hashtag
    for fname in os.listdir(os.getcwd()):
        if fname.startswith(hashtag):
            with open(fname,'r') as data_file:
                data=data_file.read()
                # Parse raw string since json.load() approach wasn't working
                data=data.split("\n\x00,")
            for tweet in data:
                count+=1
        
                # Tweets have a well-defined structure, so we can parse them 
                # manually (even though the JSON approach would be cleaner)
                text=tweet[tweet.find("text\":")+7:tweet.find(",\"source\"")-1]
                
                # Skip tweets that contain Unicode
                if text.find('\u')>=0:
                    continue
                else:
                    good_count+=1
                    # Tokenize and count word frequency, ignoring case
                    words = word_tokenize(text)
                    clean_words= [w.lower() for w in words if not w.lower() in set(stops+addl_stops)]
                    words_to_plot=words_to_plot+clean_words             
    
    #Create frequency histogram of 50 most common words and print summary of activity 
    fdist=FreqDist(words_to_plot)
    fdist.plot(50)
    print "for "+hashtag+' we collected '+str(count)+' tweets out of which '+str(good_count)+" will be analyzed"
    return words_to_plot
    
if __name__=='__main__':
    pass
    process_tweets("#both")
    #Example of a call-specific stopword inclusion
    process_tweets("#NBAFinals2015",['nbafinals2015'])
    process_tweets("#Warriors")

    
#66609 tweets overall, 46892 to be analyzed