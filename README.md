rss-torrent-reader
==================

This python project uses rss torrent feeds to determine torrents to download. It includes imdb csv input and html interface. This program has only been tested on Ubuntu 12.04, using python 2.7.

In constants you can can change the location of the configuration file.

run_once.sh will run the program once. 

run_webserver.sh will start a webgui you can use to choose which movies / series should be downloaded.

set_periodic_run.sh takes one argument, which represents the period in hours the program should run.

CURRENT WORKINGS
--------------------

Separate threads will retrieve and parse all provided rss links. Simultaneously all provided IMDB watchlists are retrieved and parsed as well in separate threads. Once the watchlists are parsed, the movies are updated with data from a movies and a series file locally stored. (Updating what movies and episodes of series should be downloaded.)
Once all of this is finished torrents are matched with movies and series. If succesfull these matches will be handled by handlers (Currently only a torrent file downloader is available). Matches that are succesfully handled (Only one handler needs to be succesful) will change the status of the movies and series, which are subsequently written to file again.

TODO
---------------------

Handlers that directly interact with Bittorrent programs to start downloads.
Handler that creates a new file that acts as a rss feed.
Handler that notifies user via email or other communication method.

Current program only uses newly created torrents. Older movies and series will need active searches.

INSTALL
---------------------

There is nothing to install, but you should take care to configure your configuration file (and the reference to it in the constants file).
Also in case you want to run this program periodically you should run set_periodic_run.sh.