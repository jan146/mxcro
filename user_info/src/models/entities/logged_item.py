import mongoengine as me

class LoggedItem(me.Document):
    timestamp: float = me.FloatField()
    quantity: float = me.FloatField()
    user_id: str = me.StringField()
    food_item_id: str = me.StringField()

