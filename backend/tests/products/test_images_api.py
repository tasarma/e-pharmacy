import pytest
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile
from products.models import ProductImage
from tenants.context import set_tenant_context

@pytest.mark.django_db
class TestProductImageAPI:
    """Test Product Image API endpoints."""

    @pytest.fixture
    def client(self):
        return APIClient()

    @pytest.fixture
    def image_file(self):
        return SimpleUploadedFile(
            name='test_image.jpg',
            content=b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x05\x04\x04\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b',
            content_type='image/jpeg'
        )

    def test_list_images(self, client, manager, product):
        """Test listing images for a product."""
        client.force_authenticate(user=manager)
        
        # Create a dummy image
        with set_tenant_context(tenant=manager.tenant):
            ProductImage.objects.create(
                tenant=manager.tenant,
                product=product,
                image="products/test.jpg",
                alt_text="Test Image"
            )

        response = client.get(
            f'/api/products/images/',
            HTTP_HOST=f"{manager.tenant.subdomain}.example.com"
        )

        assert response.status_code == 200
        assert len(response.data) > 0

    def test_upload_image(self, client, manager, product, image_file):
        """Test uploading a new image."""
        client.force_authenticate(user=manager)

        response = client.post(
            '/api/products/images/',
            {
                'product': product.id,
                'image': image_file,
                'alt_text': 'New Upload',
                'is_primary': True
            },
            format='multipart',
            HTTP_HOST=f"{manager.tenant.subdomain}.example.com"
        )

        assert response.status_code == 201
        assert response.data['alt_text'] == 'New Upload'
        assert response.data['is_primary'] is True

    def test_delete_image(self, client, manager, product):
        """Test deleting an image."""
        client.force_authenticate(user=manager)
        
        with set_tenant_context(tenant=manager.tenant):
            image = ProductImage.objects.create(
                tenant=manager.tenant,
                product=product,
                image="products/delete_me.jpg"
            )

        response = client.delete(
            f'/api/products/images/{image.id}/',
            HTTP_HOST=f"{manager.tenant.subdomain}.example.com"
        )

        assert response.status_code == 204
        with set_tenant_context(tenant=manager.tenant):
            assert not ProductImage.objects.filter(id=image.id).exists()
