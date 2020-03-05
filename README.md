# tweets_to_gdb
Loads tweets and dumps them to Google DB

A wrapper around twint library which
1) provides convenient API using config file
2) continuously runs and dumps new tweets. Saves last successful run and starts scrapping data from that timestamp.
3) saves data to Google data base and, optionally, to local csv file. Again, stores last successful state thus no data is missing in case internet connection breaks.
4) logs everything.
