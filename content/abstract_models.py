from django.contrib.contenttypes.models import ContentType
from django.db import models

class Leaf(models.Model):
    class Meta():
        abstract = True
    
    content_type = models.ForeignKey(
        ContentType, 
        editable=False, 
        null=True
    )
    classname = models.CharField(
        max_length=32, 
        editable=False, 
        null=True
    )
    
    def save(self, *args, **kwargs):
        if(not self.content_type):
            self.content_type = ContentType.objects.get_for_model(self.__class__)
        self.classname = self.__class__.__name__
        super(Leaf, self).save(*args, **kwargs)
    
    def as_leaf_class(self):
        """
        Inspired by http://www.djangosnippets.org/snippets/1031/
        """
        try:
            return self.__getattribute__(self.classname.lower())
        except AttributeError:
            content_type = self.content_type
            model = content_type.model_class()
            if(model == ModelBase):
                return self
            return model.objects.get(id=self.id)
