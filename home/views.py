# -*- coding: utf-8 -*-

from django.conf import settings
from django.shortcuts import render_to_response
from embed.utils import Embed
from django.utils.safestring import mark_safe

def home(request):
	cadena = 've este video http://www.youtube.com/watch?v=JFk30UFo2J8 que es un harlem shake, o sino este que es de Mickel Jackson https://youtu.be/THgLyTucjmk y este que es un tuit https://twitter.com/#!/twitter/status/99530515043983360. También este slideshare http://www.slideshare.net/haraldf/business-quotes-for-2011'

	Embed.consumer_key = settings.AUTH_TWITTER_EMBED_CONSUMER_KEY
	Embed.consumer_secret = settings.AUTH_TWITTER_EMBED_CONSUMER_SECRET
	Embed.oauth_token = settings.AUTH_TWITTER_TOKEN
	Embed.oauth_token_secret = settings.AUTH_TWITTER_TOKEN_SECRET

	# youtube = Embed.get_youtube_embed(string=cadena)
	# twitter = Embed.get_twitter_embed(string=cadena)
	# slideshare = Embed.get_slideshare_embed(string=cadena)

	embed = Embed.get_all(string=cadena)

	return render_to_response('index.html', {'youtube': embed})
