import logging

from photologue.models import PhotoSize


logger = logging.getLogger("logger")

print "zxxxxxxxxxxxxxxxx"
logger.info("Patching PhotoSize.name max_length")
PhotoSize._meta.get_field("name").max_length = 255
