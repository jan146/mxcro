from enum import Enum
import mongoengine as me

class Gender(Enum):
    MALE = "m"
    FEMALE = "f"

class ActivityLevel(Enum):
    SEDENTARY = "sedentary"
    LIGHT = "light"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"
    EXTREME = "extreme"

class UserInfo(me.Document):
    username: str = me.StringField(required=True, unique=True)
    age: int = me.IntField()
    height: float = me.FloatField()
    weight: float = me.FloatField()
    gender: Gender = me.EnumField(Gender)
    activity_level: ActivityLevel = me.EnumField(ActivityLevel)

