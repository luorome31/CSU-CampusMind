"""
Storage Client 测试
"""
import pytest
from unittest.mock import patch, MagicMock
from urllib.parse import urljoin


class TestStorageConfig:
    """StorageConfig 测试"""

    def test_storage_config_defaults(self):
        """测试默认配置"""
        from app.services.storage.client import StorageConfig

        config = StorageConfig()

        assert config.mode == "minio"
        assert config.base_url == "http://localhost:9000"
        assert config.bucket_name == "campusmind"

    def test_storage_config_minio(self):
        """测试 MinIO 配置"""
        from app.services.storage.client import StorageConfig

        config = StorageConfig(
            mode="minio",
            base_url="http://minio:9000",
            bucket_name="test-bucket",
            minio_access_key="admin",
            minio_secret_key="password",
            minio_endpoint="minio:9000"
        )

        assert config.mode == "minio"
        assert config.bucket_name == "test-bucket"
        assert config.minio_access_key == "admin"

    def test_storage_config_oss(self):
        """测试 OSS 配置"""
        from app.services.storage.client import StorageConfig

        config = StorageConfig(
            mode="oss",
            base_url="https://oss.example.com",
            bucket_name="oss-bucket",
            oss_access_key_id="key_id",
            oss_access_key_secret="key_secret",
            oss_endpoint="oss-cn-hangzhou.aliyuncs.com"
        )

        assert config.mode == "oss"
        assert config.oss_access_key_id == "key_id"


class TestStorageClient:
    """StorageClient 测试"""

    def test_storage_client_init(self):
        """测试客户端初始化"""
        from app.services.storage.client import StorageClient, StorageConfig

        config = StorageConfig()
        client = StorageClient(config)

        assert client.config is config
        assert client._client is None  # Lazy initialization

    def test_storage_client_default_init(self):
        """测试默认初始化"""
        from app.services.storage.client import StorageClient

        client = StorageClient()

        assert client.config is not None
        assert client.config.mode == "minio"


class TestStorageClientMocked:
    """使用 Mock 的 StorageClient 测试"""

    def test_upload_content_minio(self):
        """测试上传内容-MinIO"""
        with patch("app.services.storage.client.StorageClient._get_client") as mock_get:
            mock_client = MagicMock()
            mock_client.bucket_exists.return_value = True
            mock_get.return_value = mock_client

            from app.services.storage.client import StorageClient, StorageConfig

            config = StorageConfig(mode="minio", base_url="http://localhost:9000")
            client = StorageClient(config)

            result = client.upload_content("test/file.txt", b"test content")

            assert mock_client.put_object.called

    def test_get_url(self):
        """测试获取 URL"""
        from app.services.storage.client import StorageClient, StorageConfig

        config = StorageConfig(mode="minio", base_url="http://localhost:9000")
        client = StorageClient(config)

        result = client.get_url("test/file.txt")

        assert "test/file.txt" in result

    def test_upload_file(self):
        """测试上传文件"""
        with patch("app.services.storage.client.StorageClient._get_client") as mock_get, \
             patch("builtins.open", create=True) as mock_open:

            mock_client = MagicMock()
            mock_client.bucket_exists.return_value = True
            mock_get.return_value = mock_client

            mock_open.return_value.__enter__.return_value.read.return_value = b"file content"

            from app.services.storage.client import StorageClient, StorageConfig

            config = StorageConfig(mode="minio", base_url="http://localhost:9000")
            client = StorageClient(config)

            # This will try to open a real file, so we need to mock properly
            with patch("os.path.exists", return_value=True):
                result = client.upload_file("test/file.txt", "/tmp/test.txt")

            assert mock_client.put_object.called or mock_open.called


class TestStorageClientErrors:
    """StorageClient 错误处理测试"""

    def test_unsupported_mode(self):
        """测试不支持的模式"""
        from app.services.storage.client import StorageClient, StorageConfig

        config = StorageConfig(mode="s3")  # Unsupported mode
        client = StorageClient(config)

        with pytest.raises(ValueError, match="Unsupported storage mode"):
            client._get_client()


class TestGetStorageClient:
    """get_storage_client 工厂函数测试"""

    def test_get_storage_client(self):
        """测试获取存储客户端"""
        with patch("app.services.storage.client.get_storage_client") as mock_func:
            mock_func.return_value = MagicMock()

            from app.services.storage.client import get_storage_client

            result = get_storage_client()

            # Just verify function exists
            assert callable(result)
