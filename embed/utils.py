# -*- coding: utf-8 -*-

import re
import requests
import urllib

from requests.auth import OAuth1

class Result(object):

	def __init__(self):
		self.string = str()
		self.status_code = list()
		self.id = list()
		self.service = list()
		self.embed_code = list()


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

		result = Result()

		if len(ids) > 0:
			
			width = cls.config['width']
			height = cls.config['height']
			params = urllib.urlencode(cls.config)

			for id in ids:
				html = '<div class="video-container"><iframe width="%s" height="%s" src="http://www.youtube.com/embed/%s?%s" frameborder="0" allowfullscreen></iframe></div>' % (width, height, id, params)
				string = re.sub(r'http[s]?://(%s)%s'%(cls.youtube_pattern_search, id), html, string)
				result.status_code.append(200)
				result.id.append(id)
				result.service.append('youtube')
				result.embed_code.append(html)

			result.string = string

		return result


	@classmethod
	def get_twitter_embed_by_id(cls, id, **kwargs):

		result = Result()

		auth = OAuth1(unicode(cls.consumer_key), unicode(cls.consumer_secret), unicode(cls.oauth_token), unicode(cls.oauth_token_secret), signature_type="auth_header")
		kwargs['id'] =  id

		r = requests.get(cls.twitter_embed_url, auth=auth, params=kwargs)

		result.status_code.append(r.status_code)
		result.id.append(id)
		result.service.append('twitter')
		result.embed_code.append(r.json['html'])

		return result

	@classmethod
	def get_twitter_embed(cls, string):
		ids = cls._get_url_id(string, cls.twitter_pattern_search)
		
		try:
			string = string.decode('utf-8')
		except :
			pass

		result = Result()

		auth = OAuth1(unicode(cls.consumer_key), unicode(cls.consumer_secret), unicode(cls.oauth_token), unicode(cls.oauth_token_secret), signature_type="auth_header")

		for id in ids:
			params = dict()
			params = cls.config
			params['id'] = id

			r = requests.get(cls.twitter_embed_url, auth=auth, params=params)
			embed_code = r.json['html']
			string = re.sub(r'http[s]?://(%s)%s'%(cls.twitter_pattern_search, id), embed_code, string)

			result.status_code.append(r.status_code)
			result.id.append(id)
			result.service.append('twitter')
			result.embed_code = embed_code

		result.string = string

		return result

	@classmethod 
	def get_slideshare_embed(cls, string):
		ids = cls._get_url_id(string, cls.slideshare_pattern_search)

		try:
			string = string.decode('utf-8')
		except :
			pass

		result = Result()

		for id in ids:

			params = dict()
			params['url'] = "http://www.slideshare.net/" + id
			params['format'] = 'json'
			params['maxwidth'] = cls.config['width']
			params['maxheight'] = cls.config['height']
			
			r = requests.get(cls.slideshare_embed_url, params=params)

			embed_code = '<div class="slideshare-container">' + r.json['html'] + '</div>'
			string = re.sub(r'http[s]?://(%s)%s'%(cls.slideshare_pattern_search, id), embed_code, string)

			result.status_code.append(r.status_code)
			result.id.append(id)
			result.service.append('slideshare')
			result.embed_code.append(embed_code)

		
		result.string = string
		
		return result


	@classmethod
	def get_all(cls, string):

		result = Result()

		youtube = cls.get_youtube_embed(string=string)
		twitter = cls.get_twitter_embed(string= youtube.string)
		slideshare = cls.get_slideshare_embed(string=twitter.string)

		result.string = slideshare.string
		result.status_code = youtube.status_code + twitter.status_code + slideshare.status_code
		result.id = youtube.id + twitter.id + slideshare.id
		result.service = youtube.service + twitter.service + slideshare.service
		result.embed_code = youtube.embed_code + twitter.service + slideshare.embed_code

		return result


