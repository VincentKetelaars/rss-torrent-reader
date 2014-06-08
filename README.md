rss-torrent-reader
==================

This python project uses rss torrent feeds to find torrents to download base on imdb csv input. The HTML interface allows you to designate movies / series to be downloaded or not. You will need python 2.7 to run the program. It has successfully been tested on Ubuntu 12.04 and Windows 8.

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

Because IMDB has introduced captchas, in order to automatically retrieve the imdb watchlist we need to solve these. The [tesseract](https://code.google.com/p/tesseract-ocr/) is open source character recognition software that can read these captchas, albeit with varying results. 

In the *src/general/constants.py* file you can set *TESSERACT_ON* to True or False, indicating whether you would like to use it. In order to use it you will have to install it from the aformentioned website. To enhance the reading process I advice you to also create a new file in the *tessdata/configs/* directory and put its name in the *TESSERACT_CONFIG_FILE* variable. In this file put the following line:

tessedit_char_whitelist abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ

More information on this optimization [here](http://stackoverflow.com/a/2983295/1444854)

Then:
- Take care to configure your configuration file 
- Set the path to that configuration file in *src.general.constants.py* 
- To run this program periodically you should run *set_periodic_run.sh* with an integer argument indicating that the program should run every so many hours

###RUN

- *run_once.sh* will run the program once
- *run_webserver.sh* will start a webgui you can use to choose which movies / series should be downloaded, or to set up the configuration.
- *set_periodic_run.sh* takes one argument, which represents the period in hours the program should run.
