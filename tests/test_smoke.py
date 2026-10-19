from config import celery_app


def test_admin_login_page_opens(client):
    response = client.get("/admin/login/")

    assert response.status_code == 200


def test_celery_reads_django_settings():
    assert celery_app.conf.task_always_eager is True
