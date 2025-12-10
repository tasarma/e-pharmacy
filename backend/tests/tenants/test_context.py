import pytest
from tenants.context import (
    get_current_tenant,
    set_tenant_context,
    tenant_context_disabled,
    get_state
)
from tenants.exceptions import TenantError


@pytest.mark.django_db
class TestTenantContext:
    """Test tenant context management."""
    
    def test_get_current_tenant_without_context(self):
        """Test getting tenant without context raises error."""
        with pytest.raises(TenantError) as exc:
            get_current_tenant()
        
        assert "required" in str(exc.value).lower()
    
    def test_set_tenant_context(self, tenant):
        """Test setting tenant context."""
        with set_tenant_context(tenant=tenant):
            current = get_current_tenant()
            assert current == tenant
    
    def test_context_restored_after_exit(self, tenant):
        """Test context is restored after exiting."""
        with set_tenant_context(tenant=tenant):
            pass
        
        with pytest.raises(TenantError):
            get_current_tenant()
    
    def test_tenant_context_disabled(self, tenant):
        """Test disabling tenant enforcement."""
        with set_tenant_context(tenant=tenant):
            with tenant_context_disabled():
                state = get_state()
                assert state["enabled"] is False
    
    def test_nested_contexts(self, tenant, other_tenant):
        """Test nested tenant contexts."""
        with set_tenant_context(tenant=tenant):
            assert get_current_tenant() == tenant
            
            with set_tenant_context(tenant=other_tenant):
                assert get_current_tenant() == other_tenant
            
            # Restored to outer context
            assert get_current_tenant() == tenant
