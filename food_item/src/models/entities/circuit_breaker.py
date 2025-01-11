from enum import Enum
import mongoengine as me

class CircuitBreakerState(Enum):
    OPEN = "open"
    CLOSED = "closed"
    HALF_OPEN = "half_open"

class CircuitBreaker(me.Document):
    state: CircuitBreakerState = me.EnumField(CircuitBreakerState, required=True)
    event_name: str = me.StringField(required=True)
    timestamp: float = me.FloatField(required=True)

