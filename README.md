#Nick Hamlin - Assignment 2

##Summary of Outputs
- **listener.py**: Run this code first to process tweets from the twitter firehose for the relevant hashtags
- **create_histograms.py**: Once tweets are gathered, this file is run to read through the chunked files created by listener.py and create frequency histograms of the top 50 most used terms
- Three word frequency histograms (saved as .png files) for each type of tweet (#Warriors, #NBAFinals2015, and Both)
- All chunked sets of tweets are stored in [this AWS bucket](https://s3-us-west-2.amazonaws.com/hamlin-mids-assignment2).  For convenience, a file containing a list of direct links to each individual chunk (links_to_data.txt) is included in this repo as well.


##Program Design
Despite the time crunch it created, I wanted to use the Twitter firehose to
gather tweets in realtime.  To do this, I used the Tweepy library’s
StreamListener class to monitor the firehose for tweets that contained either
the #NBAFinals2015 or #Warriors hashtag.  When a relevant tweet is found, the
program checks which hashtag(s) it contains and appends it to one of three
active json files (one for each hashtag, and a third for tweets that contain
both. Since the program gathers data in real-time and there was limited activity after the deluge of tweets surrounding the final game of the series, during office hours Luis confirmed that I didn’t need to let the program run for an additional several days after the fact and that the volume of tweets I gathered during this peak activity was sufficient.

##Chunking
Tweets will be recorded in the same file until a threshold of 5000 tweets is
reached.  At this point, the file will be closed, a new file for that hashtag
will be opened, and the tweet logging can continue.  Each chunked file is
named according to the hashtag it represents and the timestamp when it was
created.  This chunking strategy was chosen over other approaches (like
chunking by a particular time range) because we’re collecting live data from
the firehose, not stored data for a chosen search query via the REST API.
This means that it’s more critical to effectively deal with the high velocity
and volume of information than it is to be able to rebuild a file for a
particular date range, which would require a different implementation. For scalability purposes, the 5000 tweet threshold can be easily increased if larger size chunks are desired.

##Resilency
This program takes several steps to ensure resiliency.  First, whenever an
output file reaches the preset threshold of tweets, it is automatically
uploaded to an S3 bucket.  This prevents all critical data from being stored
only in one place.  The same upload behavior occurs in the event that the
program encounters a fatal error.  The WHILE loop structure in the main
function allows for robust handling of rate limiting and timeout issues
created by restrictions imposed by the Twitter API itself.  This came in handy
during the final minutes of game 6, when tweets about the Warriors were coming
in at a rate too fast for the firehose to allow unfettered access.  When this
occurs, the program will note the issue in a log file and pause for 60 seconds
before trying to reconnect.  Other important events are also tracked via a log
file, including when transitions between chunks occur.  Each of these events
is timestamped to facilitate debugging.

##Word Frequency Histograms
In creating word frequency histograms for each tweet corpus, the list of
common english stop words included in Python’s NLTK package have been
excluded.  In addition, a custom set of stop words relating to common twitter
jargon (Like “RT”,”MT”, etc.) as well as tweets containing complex unicode
characters have also been excluded.  This eliminates much of the noise from
the histograms and allows us a more streamlined understanding of the actual
tweet content.  Out of 66609 total tweets collected, this leaves 46892 to be
analyzed.  Finally, all words are converted to lowercase before creating the
final histogram.  This causes “WARRIORS” and “warriors” to be counted as the
same term, further eliminating excess noise.  Except in the case of #Warriors
(because the content of the hashtag is also the team name and important to the
meaning of the histogram) the hashtags themselves are also excluded.  The
result is a frequency distribution that minimizes noise and focuses on the
most meaningful set of words (those that are neither too frequent nor too
rare). To ensure a representative but not overly cumbersome visualization, I chose to plot the top 50 most frequent words remaining after applying the exclusions mentioned above.

##Packages used
####Base Python:
- json
- os
- time
- sys

####Third Party:
- NLTK
- Tweepy
- Boto

##Other Useful References:
- [http://badhessian.org/2012/10/collecting-real-time-twitter-data-with-the-
streaming-api/](http://badhessian.org/2012/10/collecting-real-time-twitter-
data-with-the-streaming-api/)
- [http://www.pythoncentral.io/introduction-to-tweepy-twitter-for-
python/](http://www.pythoncentral.io/introduction-to-tweepy-twitter-for-
python/)


