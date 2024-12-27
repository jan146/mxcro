import mongoengine as me

class FoodItem(me.Document):
    name: str = me.StringField()
    calories: float = me.FloatField()
    weight_g: float = me.FloatField()
    fat_total: float = me.FloatField()
    fat_saturated: float = me.FloatField()
    protein: float = me.FloatField()
    carbohydrates: float = me.FloatField()
    fiber: float = me.FloatField()
    sugar: float = me.FloatField()
    sodium: float = me.FloatField()
    potassium: float = me.FloatField()
    cholesterol: float = me.FloatField()

