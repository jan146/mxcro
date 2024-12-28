import mongoengine as me

class LoggedItem(me.Document):
    timestamp: float = me.FloatField(required=True)
    quantity: float = me.FloatField(required=True)
    user_id: str = me.StringField(required=True)
    food_item_id: str = me.StringField(required=True)

