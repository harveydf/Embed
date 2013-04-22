import re
import requests
import urllib

from django.utils.safestring import mark_safe
from requests.auth import OAuth1
from embed.models import EmbedCache


class Embed(object):


	consumer_key = None
	consumer_secret = None
	oauth_token = None
	oauth_token_secret = None

	youtube_pattern_search = 'www\.youtube\.com/watch\?v=|youtu\.be/'

	twitter_pattern_search = 'twitter\.com/twitter/status/|twitter\.com/#!/twitter/status/'
	twitter_embed_url = 'https://api.twitter.com/1.1/statuses/oembed.json'

	slideshare_pattern_search = 'www\.slideshare\.net/'
	slideshare_embed_url = 'http://www.slideshare.net/api/oembed/2'

	config = {
		'width': '400',
		'height': '300'
	}

	@classmethod
	def _get_url_id(cls, string, pattern):
		finded = re.findall(r'http[s]?://(%s)([\w/\-#]+)' % pattern, string)

		res = list()

		if len(finded) > 0:
			for url, id in finded:
				res.append(id)

		return res

	@classmethod
	def get_youtube_embed(cls, string):
		ids = cls._get_url_id(string, cls.youtube_pattern_search)

		try:
			string = string.decode('utf-8')
		except :
			pass

		width = cls.config['width']
		height = cls.config['height']
		params = urllib.urlencode(cls.config)

		for id in ids:
			video, created = EmbedCache.objects.get_or_create(service="youtube", embed_id=id)

			if video.embed_code is None:
				video.embed_code = '<div class="video-container"><iframe width="%s" height="%s" src="http://www.youtube.com/embed/%s?%s" frameborder="0" allowfullscreen></iframe></div>' % (width, height, id, params)
				video.save()

			string = re.sub(r'http[s]?://(%s)%s'%(cls.youtube_pattern_search, id), video.embed_code, string)

		return mark_safe(string)


	@classmethod
	def get_twitter_embed_by_id(cls, id, **kwargs):

		tweet, created = EmbedCache.objects.get_or_create(service="twitter", embed_id=id)

		if tweet.embed_code is None:
			auth = OAuth1(unicode(cls.consumer_key), unicode(cls.consumer_secret), unicode(cls.oauth_token), unicode(cls.oauth_token_secret), signature_type="auth_header")
			kwargs['id'] =  id

			r = requests.get(cls.twitter_embed_url, auth=auth, params=kwargs)

			if r.status_code == 200:
				tweet.embed_code = r.json['html']
				tweet.save()

		return mark_safe(tweet.embed_code)


	@classmethod
	def get_twitter_embed(cls, string):
		ids = cls._get_url_id(string, cls.twitter_pattern_search)
		
		try:
			string = string.decode('utf-8')
		except :
			pass

			
		for id in ids:
			tweet, created = EmbedCache.objects.get_or_create(service="twitter", embed_id=id)

			if tweet.embed_code is None:
				params = dict()
				params = cls.config
				params['id'] = id

				auth = OAuth1(unicode(cls.consumer_key), unicode(cls.consumer_secret), unicode(cls.oauth_token), unicode(cls.oauth_token_secret), signature_type="auth_header")
				r = requests.get(cls.twitter_embed_url, auth=auth, params=params)
				
				if r.status_code == 200:
					tweet.embed_code = r.json['html']
					tweet.save()

			string = re.sub(r'http[s]?://(%s)%s'%(cls.twitter_pattern_search, id), tweet.embed_code, string)

		return mark_safe(string)

	@classmethod 
	def get_slideshare_embed(cls, string):
		ids = cls._get_url_id(string, cls.slideshare_pattern_search)

		try:
			string = string.decode('utf-8')
		except :
			pass

		for id in ids:
			slide, created = EmbedCache.objects.get_or_create(service="slideshare", embed_id=id)

			if slide.embed_code is None:
				params = dict()
				params['url'] = "http://www.slideshare.net/" + id
				params['format'] = 'json'
				params['maxwidth'] = cls.config['width']
				params['maxheight'] = cls.config['height']
				
				r = requests.get(cls.slideshare_embed_url, params=params)

				if r.status_code == 200:
					slide.embed_code = '<div class="slideshare-container">' + r.json['html'] + '</div>'
					slide.save()

			string = re.sub(r'http[s]?://(%s)%s'%(cls.slideshare_pattern_search, id), slide.embed_code, string)
		
		return mark_safe(string)


	@classmethod
	def get_all(cls, string):
		string = cls.get_youtube_embed(string=string)
		string = cls.get_twitter_embed(string=string)
		string = cls.get_slideshare_embed(string=string)

		return string


