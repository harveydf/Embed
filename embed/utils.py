import re
import requests
import urllib

class Result(object):

	def __init__(self):
		self.string = list()
		self.status_code = list()
		self.id = list()
		self.service = list()
		self.embed_code = list()


class Embed(object):

	api_twitter_url = 'https://api.twitter.com/'
	api_twitter_embed_url = '/statuses/oembed.json'
	api_twitter_version = '1.1'

	consumer_key = None
	consumer_secret = None
	oauth_token = None
	oauth_token_secret = None

	youtube_pattern_search = 'www\.youtube\.com/watch\?v=|youtu\.be/'

	slideshare_pattern_search = 'www\.slideshare\.net/'
	slideshare_embed_url = 'http://www.slideshare.net/api/oembed/2'

	config = {
		'width': '400',
		'height': '300'
	}

	@classmethod
	def _get_url_id(cls, string, pattern):
		finded = re.findall(r'http[s]?://(%s)([a-zA-Z0-9$-_@.&+!*\,]+)' % pattern, string)

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
				result.string.append(string)
				result.status_code.append(200)
				result.id.append(id)
				result.service.append('youtube')
				result.embed_code.append(html)

		return result


	@classmethod
	def get_twitter_embed(cls, id, **kwargs):

		result = Result()

		auth = OAuth1(unicode(cls.consumer_key), unicode(cls.consumer_secret), unicode(cls.oauth_token), unicode(cls.oauth_token_secret), signature_type="auth_header")
		kwargs['id'] =  id

		r = requests.get(cls.api_twitter_url + cls.api_twitter_version + cls.api_twitter_embed_url, auth=auth, params=kwargs)

		result.status_code.append(r.status_code)
		result.id.append(id)
		result.service.append('twitter')
		result.embed_code.append(r.json['html'])

		return result

	@classmethod 
	def get_slideshare_embed(cls, string):
		ids = cls._get_url_id(string, cls.slideshare_pattern_search)

		string = string.decode('utf-8')
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

			result.string.append(string)
			result.status_code.append(r.status_code)
			result.id.append(id)
			result.service.append('slideshare')
			result.embed_code.append(embed_code)

		return string


#### TODO CAMBIAR ESTO!!
	@classmethod
	def get_all(cls, string):
		string = cls.get_youtube_embed(string=string)
		string = cls.get_slideshare_embed(string=string)
		return string


