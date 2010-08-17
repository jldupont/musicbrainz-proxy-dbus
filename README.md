Linux Musicbrainz Proxy over DBus

This application provides a proxy service over Dbus for retrieving the 'track mbid' information associated with an 'artist'/'title' pair.

DBus
====

The input signals are:

* interface: 'com.jldupont.musicbrainz.proxy'
* path: 'Tracks'
* signal name: 'qTrack'
  * param 1: ref: an opaque string that serves to identify the request
  * param 2: artist: string
  * param 3: title: string
  * param 4: priority: string ["low" | "high"]

This signal is used to 'request' information for a specific track.
When "priority=low",  this signal is used to 'prime up' the cache i.e. the requests will be put in the 'low priority' queue.  
  
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
 - v2.6: 
   - increased retry-timeout for tracks not found to 5days
   - removed "retry later" log message
   - removed" filtered" log message
 - v2.7: added "priority" option for qTrack Dbus signal
 - v2.8: fixed corner case bug
 - v2.9: significant speed increase by optimizing the central message switch with priorities, controlled bursting, filtering based on 'agent interest'
 - v2.10: fixed shutdown process
 - v2.11: minor fix in AgentThreadedBase
 - v2.20: added 'help' button and tray icon
 - v2.22: bumped priority of "show" system event

[Home](http://www.systemical.com/ "Home")
