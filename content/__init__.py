# set photosize name field max_length to 64 so we can support longer names
from photologue.models import PhotoSize
PhotoSize._meta.get_field_by_name('name')[0].max_length = 64
