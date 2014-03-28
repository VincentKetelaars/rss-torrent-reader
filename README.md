rss-torrent-reader
==================

This python project uses rss torrent feeds to find torrents to download base on imdb csv input. The HTML interface allows you to designate movies / series to be downloaded or not. This program has only been tested on Ubuntu 12.04, using python 2.7.

### CURRENT

Separate threads will retrieve and parse all provided rss links. Additionally rss feeds can be created as well to actively search for movies and series. Simultaneously all provided IMDB watchlists are retrieved and parsed as well in separate threads. Once the watchlists are parsed, the movies are updated with data from a movies and a series file locally stored. (Updating what movies and episodes of series should be downloaded.)
Once all of this is finished, torrents are matched with movies and series. If succesfull these matches will be handled by handlers. (Downloader, RSSCreator and Email are available now) Matches that are succesfully handled (All primary handlers need to be successfull) will change the status of the movies and series, which are subsequently written to their respective files again.

### TODO

- Handlers that directly interact with Bittorrent programs to start downloads.
- Handlers for other communication methods than email
- Allow for multiple seasons / episode in one torrent"

### INSTALL

You can get the repository with:

```sh
git clone --recursive git://github.com/VincentKetelaars/rss-torrent-reader.git
```

Make sure you add the recursive argument since this project makes use of another.

There is nothing to install, but:
- Take care to configure your configuration file 
- Set the path to that configuration file in *src.general.constants.py* 
- To run this program periodically you should run *set_periodic_run.sh* with an integer argument indicating that the program should run every so many hours

###RUN

- *run_once.sh* will run the program once
- *run_webserver.sh* will start a webgui you can use to choose which movies / series should be downloaded, or to set up the configuration.
- *set_periodic_run.sh* takes one argument, which represents the period in hours the program should run.