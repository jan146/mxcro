import mongoengine as me

class UserInfo(me.Document):
    username: str = me.StringField()
    age: int = me.IntField()
    height: float = me.FloatField()
    weight: float = me.FloatField()

