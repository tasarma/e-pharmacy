from django.db import transaction, connection
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from typing import Dict, Optional
import structlog

from .models import Tenant, TenantSettings
from .context import set_tenant_context, tenant_context_disabled

logger = structlog.get_logger(__name__)
User = get_user_model()


class TenantOnboardingService:
    """
    Handles secure tenant creation with rollback on failure.
    Creates tenant + manager user (tenant-level admin role).
    """

    @staticmethod
    @transaction.atomic
    def create_tenant_with_manager(
        name: str,
        subdomain: str,
        manager_email: str,
        manager_password: str,
        manager_first_name: str = "",
        manager_last_name: str = "",
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Create tenant + manager user atomically.
        
        Returns:
            {
                'tenant': Tenant instance,
                'manager_user': User instance,
                'success': bool,
                'message': str
            }
        """
        
        # Use savepoint for nested rollback safety
        sid = transaction.savepoint()
        
        try:
            # 1. Create tenant (validation happens in model.save())
            with tenant_context_disabled():
                tenant = Tenant.objects.create(
                    name=name,
                    subdomain=subdomain.lower().strip(),
                    active=False
                )
                
                logger.info(
                    "tenant_created",
                    tenant_id=str(tenant.id),
                    subdomain=tenant.subdomain
                )
            
            # 2. Create manager user within tenant context
            with set_tenant_context(tenant=tenant):

                # Check for existing email in THIS tenant
                if User.objects.filter(email=manager_email).exists():
                    raise ValidationError(
                        f"Email {manager_email} already exists in tenant"
                    )
                
                manager_user = User.objects.create_user(
                    email=manager_email,
                    password=manager_password,
                    role='manager', 
                    is_staff=False,
                    is_active=False,
                    first_name=manager_first_name,
                    last_name=manager_last_name,
                    tenant=tenant
                )
                
                logger.info(
                    "tenant_manager_created",
                    tenant_id=str(tenant.id),
                    user_id=str(manager_user.id),
                    email=manager_email
                )
            
            # 3. Initialize tenant data (products, categories, settings, etc.)
            TenantOnboardingService._initialize_tenant_data(tenant, metadata)
            
            transaction.savepoint_commit(sid)
            
            return {
                'tenant': tenant,
                'manager_user': manager_user,
                'success': True,
                'message': f'Tenant {subdomain} created successfully'
            }
            
        except ValidationError as e:
            transaction.savepoint_rollback(sid)
            logger.error(
                "tenant_onboarding_validation_failed",
                subdomain=subdomain,
                error=str(e)
            )
            raise
            
        except Exception as e:
            transaction.savepoint_rollback(sid)
            logger.error(
                "tenant_onboarding_failed",
                subdomain=subdomain,
                error=str(e),
                exc_info=True
            )
            raise ValidationError(f"Failed to create tenant: {str(e)}")
    
    @staticmethod
    def _initialize_tenant_data(tenant: Tenant, metadata: Optional[Dict] = None) -> None:
        """Create default settings for new tenant."""
        with set_tenant_context(tenant=tenant):
            settings_data = {
                'tenant': tenant,
                'store_name': metadata.get('store_name', tenant.name) if metadata else tenant.name,
                'email': metadata.get('email', f'contact@{tenant.subdomain}.example.com') if metadata else f'contact@{tenant.subdomain}.example.com',
                'phone_number': metadata.get('phone_number', '') if metadata else '',
                'allow_guest_checkout': True,
                'require_email_verification': True,
            }
            
            TenantSettings.objects.create(**settings_data)
            
            logger.info(
                "tenant_settings_initialized",
                tenant_id=str(tenant.id)
            )
