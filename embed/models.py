from django.db import models

class EmbedCache(models.Model):
	service = models.CharField(max_length=255)
	embed_id = models.CharField(max_length=255)
	embed_code = models.TextField(blank=True, null=True, default=None)

	def __unicode__(self):
		return self.embed_id