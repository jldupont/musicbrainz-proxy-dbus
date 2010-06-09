Linux Musicbrainz Proxy over DBus

This application provides a proxy service over Dbus for retrieving the 'track mbid' information associated with an 'artist'/'title' pair.

DBus
====

The input signal is:

* interface: 'com.jldupont.musicbrainz.proxy'
* path: 'Tracks'
* signal name: 'qTrack'
  * param 1: ref: an opaque string that serves to identify the request
  * param 2: artist: string
  * param 3: title: string
  
The resulting output signal if the track is either found in the cache or through the Musicbrainz webservice:

* interface: com.jldupont.musicbrainz.proxy
* path: 'Tracks'
* signal name: 'Tracks'
  * param 1: source: string (either 'cache' or 'mb')
  * param 2: ref 
  * param 3: list of track details: aa{sv}
  
In other words, the resulting signal contains a 'list' of dictionaries of 'details'


Track Details
-------------

A dictionary containing the following keys:

 - "artist_name"
 - "track_name"
 - "artist_mbid"
 - "track_mbid"
 - "mb_artist_name"
 - "mb_track_name"

Managed Files
=============

This application manages the following files:

 - ~/musicbrainz-proxy.log :    log file
 - ~/musicbrainz-proxy.sqlite : cache database file


Installation
============
There are 2 methods:

1. Use the Ubuntu Debian repository [jldupont](https://launchpad.net/~jldupont/+archive/phidgets)  with the package "rbsynclastfm"

2. Use the "Download Source" function of this git repo and use "sudo make install"

Dependencies
============

* python-musicbrainz2

History
=======

 - v2.3: the 'cache' in the application won't return 'Tracks' signal on a 'cache miss'
 - v2.4: added statistics "total records", "records with track_mbid", "job queue depth"
 - v2.5: added "artist name" based filtering (common cases) & "filtered" statistics
 
[Home](http://www.systemical.com/ "Home")
