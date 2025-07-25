from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any, Dict, Generator, Optional

from .exceptions import TenantError

state: ContextVar[Optional[Dict[str, Any]]] = ContextVar("tenant-state", default=None)


def get_state() -> Dict[str, Any]:
    """
    Get the current tenant context state.
    Default: {"enabled": True, "tenant": None}
    """
    return state.get() or {"enabled": True, "tenant": None}


def get_current_tenant() -> Any:
    """
    Return the current tenant if tenant enforcement is enabled.

    Raises:
        TenantError: if enforcement is enabled but no tenant is set.
    """
    current_state = get_state()

    if current_state["enabled"] and current_state["tenant"] is None:
        raise TenantError("Tenant is required in context")
    return current_state["tenant"]


@contextmanager
def set_tenant_context(
    tenant: Optional[Any] = None, enabled: bool = True
) -> Generator[None, None, None]:
    """
    Temporarily set the tenant context.
    """
    previous_state = get_state()

    new_state = previous_state.copy()
    new_state["enabled"] = enabled
    new_state["tenant"] = tenant

    token = state.set(new_state)
    try:
        yield
    finally:
        state.reset(token)


@contextmanager
def tenant_context_disabled() -> Generator[None, None, None]:
    """
    Temporarily disable tenant enforcement.
    """
    with set_tenant_context(enabled=False):
        yield
