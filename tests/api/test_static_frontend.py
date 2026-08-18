def test_static_frontend_is_served_at_root(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "AI ICP Qualification Engine" in response.text


def test_static_assets_are_served(client):
    css = client.get("/css/style.css")
    js = client.get("/js/app.js")

    assert css.status_code == 200
    assert js.status_code == 200


def test_api_routes_are_not_shadowed_by_static_mount(client):
    response = client.post(
        "/api/jobs",
        json={"job_title": "Coach", "country": "France"},
    )

    assert response.status_code == 201


def test_api_health_route_is_not_shadowed_by_static_mount(client):
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
