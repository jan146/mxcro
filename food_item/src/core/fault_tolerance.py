import time
from food_item.src.models.entities.circuit_breaker import CircuitBreaker, CircuitBreakerState

TIMEOUT_SECONDS: int = 30

def get_latest_cb(event_name: str) -> CircuitBreaker | None:
    return CircuitBreaker.objects(event_name=event_name).order_by("-timestamp").first()

def get_cb_state(circuit_breaker: CircuitBreaker | None) -> CircuitBreakerState:
    if circuit_breaker is None or circuit_breaker.state == CircuitBreakerState.CLOSED:
        return CircuitBreakerState.CLOSED
    min_timestamp: float = time.time() - TIMEOUT_SECONDS
    if circuit_breaker.timestamp > min_timestamp:
        return CircuitBreakerState.OPEN
    else:
        return CircuitBreakerState.HALF_OPEN

def trip_cb(event_name: str):
    # Create new open circuit breaker entity
    circuit_breaker: CircuitBreaker = CircuitBreaker(
        state=CircuitBreakerState.OPEN,
        event_name=event_name,
        timestamp=time.time(),
    )
    circuit_breaker.save()

def update_old_open_cb():
    # If a circuit breaker has been open for >TIMEOUT_SECONDS, the change it to half-open
    min_timestamp: float = time.time() - TIMEOUT_SECONDS
    CircuitBreaker.objects(timestamp__lt=min_timestamp, state=CircuitBreakerState.OPEN).update(set__state=CircuitBreakerState.HALF_OPEN)

def update_half_open_cb(cb: CircuitBreaker, success: bool):
    # Update state of half open circuit breaker according to success of related operation
    cb.reload()
    if cb.state in [CircuitBreakerState.OPEN, CircuitBreakerState.HALF_OPEN]:
        new_state: CircuitBreakerState = CircuitBreakerState.CLOSED if success else CircuitBreakerState.OPEN
        cb.update(set__state=new_state)

