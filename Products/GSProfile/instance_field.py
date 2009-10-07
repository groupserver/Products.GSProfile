from zope.schema.interfaces import IField
from zope.interface import implements

class GSField(object):

    implements(IField)
    
    def __init__(self):
        self.default = None
        self.missing_value = None
        self.order = 0
        self.required = False
        self.description = u''
        self.readonly = False
        self.title = ''
        
    def set(instance, value):
        if self.readonly:
            raise TypeError
        else:
            raise NotImplemented
            
    def get(instance):
        raise NotImplemented
        
    def bind(instance):
        newField = GSField()
        newField.default = self.default
        newField.missing_value = self.missing_value
        newField.order = self.order
        newField.required = self.required
        newField.description = self.description
        newField.readonly = self.readonly
        newField.title = self.title
        newField.context = instance
        return newField

    def constraint(value):
        return True

    def query(object, default=None):
        raise NotImplemented

    def validate(value):
        pass


