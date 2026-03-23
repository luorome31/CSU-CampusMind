"""
Crawl Task API tests
"""
from fastapi.testclient import TestClient
from app.services.crawl.task_service import CrawlTaskService

class TestCrawlTaskAPI:
    def test_get_crawl_task(self, mock_auth):
        from app.main import app
        client = TestClient(app)
        
        # Create a task in DB with the same user_id as mock_auth
        user_id = mock_auth["user_id"]
        task = CrawlTaskService.create_task(user_id=user_id, total_urls=5)
        
        # Poll the task API
        response = client.get(f"/api/v1/crawl/tasks/{task.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task.id
        assert data["status"] == "processing"
        assert data["total_urls"] == 5
        assert data["completed_urls"] == 0

    def test_get_crawl_task_not_found(self, mock_auth):
        from app.main import app
        client = TestClient(app)
        
        response = client.get("/api/v1/crawl/tasks/nonexistent_task_id")
        assert response.status_code == 404
