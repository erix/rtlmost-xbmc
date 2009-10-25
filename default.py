#!/usr/bin/env python
# encoding: utf-8
"""
default.py

Created by Erik Simko on 2009-10-24.
Copyright (c) 2009 __MyCompanyName__. All rights reserved.
"""

import sys
import os
import xbmc
import xbmcgui
import xbmcplugin
import urllib
import re
import lib.demjson as demjson

from xml.sax.saxutils import unescape
from lib.BeautifulSoup import BeautifulSoup

# plugin constants
__plugin__ = "RTLMost"
__author__ = "erix"
__url__ = ""
__svn_url__ = ""
__credits__ = "Team XBMC"
__version__ = "0.0.1"

BASE_URL = "http://www.rtlklub.hu/most/"

def clear_escape(string):
	"""Clears the backslash escaping"""
	
	return re.sub(r'\\(.)', r'\1', string)

def get_params(paramstring):
        param=[]
        if len(paramstring)>=2:
                params=paramstring
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]
                                
        return param

def retrieve_url(url):
	""" Fetches the HTML from given URL.
		Return empty string if failed
	"""
	try:
		usock = urllib.urlopen( url )
		html = usock.read()
		usock.close()
	except:
		html = ""
		
	#return html
	# fix the fucked up encoding in original document
	return re.sub("Medi.n WebAudit RTLcsoport rtlmost.hu", "", html)


def find_episode_hash(html):
	"""
	<script type="text/javascript">
			swfobject.embedSWF("http://www.rtlklub.hu/most/player/flv_player.swf?v=3", "swfobj", "560", "413", "9.0.115", "http://www.rtlklub.hu/most/player/js/expressInstall.swf",{share:true,parameters:"./player/content/parameters.php?hash=40c27e9d90",skin:"./player/skin/skin.xml?v=2"}, {menu:false,allowFullScreen:true,allowScriptAccess:"always",wmode:"transparent",pluginspage:"http://www.macromedia.com/go/getflashplayer"}, {id:"content_object",name:"content_object"});
	</script>

	"""
	episodeHash = re.compile('\.\/player\/content\/parameters.php\?hash=(\w+)').findall(html)
	#print episodeHash[0]
	return episodeHash[0]

def get_episode(url):
	"""docstring for get_episode
	{u'configuration': 
		{u'search': u'http://www.google.com/search?q=', 
		u'description': u'Toyota Prius, Aprilia Tuono 1000R, Honda Accord 2.2 I-DTEC', 
		u'title': u'Autu00f3mu00e1nia 09-10-24', 
		u'image': u'http://www.rtlklub.hu/most/files/thumbnails/005/217/1.jpg', 
		u'outro_skipable': False, 
		u'intro_skipable': False, 
		u'intro': '', 
		u'file': [u'http://92.52.253.141/most/005/217/automania091024.mp4'], 
		u'outro': '', 
		u'intro_url': '', 
		u'outro_url': '', 
		u'id': u'5217'
	}, 
	u'share': [{u'action': u'showEmbed', u'label': u'megosztu00e1s', u'icon': u'SHARE_LINK'}], u'related': [{u'url': u'http://www.rtlklub.hu/most/5049_automania_09-10-17', u'thumbnail': u'http://www.rtlklub.hu/most/files/thumbnails/005/049/1.jpg', u'name': u'Autu00f3mu00e1nia 09-10-17'}, {u'url': u'http://www.rtlklub.hu/most/4911_automania_09-10-10', u'thumbnail': u'http://www.rtlklub.hu/most/files/thumbnails/004/911/1.jpg', u'name': u'Autu00f3mu00e1nia 09-10-10'}, {u'url': u'http://www.rtlklub.hu/most/4735_automania_09-10-03', u'thumbnail': u'http://www.rtlklub.hu/most/files/thumbnails/004/735/1.jpg', u'name': u'Autu00f3mu00e1nia 09-10-03'}, {u'url': u'http://www.rtlklub.hu/most/4493_automania_09-09-26', u'thumbnail': u'http://www.rtlklub.hu/most/files/thumbnails/004/493/1.jpg', u'name': u'Autu00f3mu00e1nia 09-09-26'}, {u'url': u'http://www.rtlklub.hu/most/4357_automania_09-09-19', u'thumbnail': u'http://www.rtlklub.hu/most/files/thumbnails/004/357/1.jpg', u'name': u'Autu00f3mu00e1nia 09-09-19'}, {u'url': u'http://www.rtlklub.hu/most/4191_automania_09-09-12', u'thumbnail': u'http://www.rtlklub.hu/most/files/thumbnails/004/191/1.jpg', u'name': u'Autu00f3mu00e1nia 09-09-12'}, {u'url': u'http://www.rtlklub.hu/most/4059_automania_09-09-05', u'thumbnail': u'http://www.rtlklub.hu/most/files/thumbnails/004/059/1.jpg', u'name': u'Autu00f3mu00e1nia 09-09-05'}], u'checkpoints': [], u'login_configuration': {u'login_description': '', u'login': u'http://www.rtlklub.hu/most/player/content/login.php', u'login_title': u'Lu00e9pj be u00e9s nu00e9zd tovu00e1bb!', u'lostpass': u'showLostPassword', u'registration': u'showRegistration'}}


	"""
	html = retrieve_url(url)
	#print html
	episodeHash = find_episode_hash(html)
	html = retrieve_url("http://www.rtlklub.hu/most/player/content/parameters.php?hash="+episodeHash)

	# unescape the backslashes
	episode = demjson.decode(html)
	return episode["configuration"]



def get_episodes(url):
	"""docstring for get_episodes"""

	html = retrieve_url(url)
	soup = BeautifulSoup(html, fromEncoding="utf-8")
	episodesHtml = soup.findAll("div", attrs={"class" : "video-img-cont-catchup cont-first"})

	""" result

	<div class="video-img-cont-catchup cont-first" id="5217">
		<div class="video-date">okt 24.<span>12:15</span></div>
		<a href="http://www.rtlklub.hu/most/5217_automania_09-10-24" class="video-img">
			<img src="http://www.rtlklub.hu/most/files/thumbnails/005/217/2.jpg" width="120" height="90" alt="AutÃ³mÃ¡nia 09-10-24" title="AutÃ³mÃ¡nia 09-10-24" />
		</a>
		<a href="javascript:void(0)" class="video-add" id="5217-0">
			<img src="http://www.rtlklub.hu/most/style/img/add_video_icon.png" alt="Add a kedvenceid kÃ¶zÃ©" title="Add a kedvenceid kÃ¶zÃ©" />
		</a>
		<div class="img-height-wide"></div>
		<h2>
			<a href="http://www.rtlklub.hu/most/5217_automania_09-10-24">AutÃ³mÃ¡nia 09-10-24</a>
		</h2>
		<p>Toyota Prius, Aprilia Tuono 1000R, Honda Accord 2.2 I-DTEC</p>
	</div>

	"""

	episodes = []
	#print len(episodesHtml)
	for episode in episodesHtml:
		episodes.append({"title":episode.h2.a.string, "url":episode.h2.a['href'], "thumb":episode.a.img['src']})
	#print episodes	
	return episodes

def get_shows():
	"""docstring for get_shows"""
	html = retrieve_url(BASE_URL)
	soup = BeautifulSoup(html, fromEncoding="utf-8")
	#print soup.prettify
	#print "Autómánia"
	showsHtml = soup.find(id="topnav04-ul").findAll("li")
	#remove the last item
	showsHtml.pop(len(showsHtml)-1)
	shows = []
	for show in showsHtml:
		shows.append({"title" : show.a.string, "url" : show.a['href']})
	return shows

def show_all_shows(shows):
	"""Adds the show list to XBMC"""
	for show in shows:
		item = xbmcgui.ListItem(label=unescape(show["title"]))
		labels ={"title" : unescape(show["title"])}
		item.setInfo(type = 'movie', infoLabels=labels)
		url = sys.argv[0]+"?mode=Episodes"+"&url="+show["url"]
		xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, item, True, len(shows))
		
def show_episodes(episodes):
	"""docstring for show_set"""
	#print get_episodes("http://www.rtlklub.hu/most/musorok/automania")

	for episode in episodes:
		episodeData = get_episode(episode["url"])

		item = xbmcgui.ListItem(label=episodeData["title"], thumbnailImage=clear_escape(episodeData["image"]))
			#label=track["track"]["trackTitle"])
			#label2=track["track"]["trackTitle"])		
		labels={
            "title": episodeData["title"],
			"descripion": episodeData["description"]
			}
		
		item.setInfo(type = 'movie', infoLabels=labels)

		xbmcplugin.addDirectoryItem(int(sys.argv[1]), clear_escape(episodeData["file"][0]), item, False, len(episodes))
	

	
def main():
	
	reload(sys); sys.setdefaultencoding('utf-8')
	xbmc.log( "[PLUGIN] '%s: version %s' initialized!" % ( __plugin__, __version__, ), xbmc.LOGNOTICE )
	
	xbmcplugin.setContent(int(sys.argv[1]), 'movie')

	params = get_params(sys.argv[2])
	mode = "AllShows"
	
	try:
		mode = params["mode"]
	except:
		pass
	
	xbmc.log( "[PLUGIN] invoke mode: %s" % mode, xbmc.LOGNOTICE )

	if mode == "AllShows":
		show_all_shows(get_shows())
	elif mode == "Episodes":
		xbmc.log( "[PLUGIN] invoke url: %s" % params["url"], xbmc.LOGNOTICE )
		show_episodes(get_episodes(params["url"]))
		
	xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )
	xbmcplugin.endOfDirectory(int(sys.argv[1]))


if __name__ == '__main__':
	main()

