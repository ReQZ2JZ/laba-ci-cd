from fastapi.testclient import TestClient
import main

client = TestClient(main.app)


def setup_function():
    main.CART.clear()
    main.ORDERS.clear()


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_products():
    response = client.get("/products")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_product_by_id():
    response = client.get("/product/0")
    assert response.status_code == 200
    assert "name" in response.json()


def test_search():
    response = client.get("/search?q=ноут")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_cart_initially_empty():
    response = client.get("/cart")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0


def test_add_to_cart():
    response = client.post("/cart/add?pid=0&qty=2")
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["item"]["pid"] == 0
    assert data["item"]["qty"] == 2


def test_add_to_cart_invalid_pid():
    response = client.post("/cart/add?pid=999&qty=1")
    assert response.status_code == 404


def test_add_to_cart_invalid_qty():
    response = client.post("/cart/add?pid=0&qty=0")
    assert response.status_code == 400


def test_clear_cart():
    client.post("/cart/add?pid=0&qty=1")
    response = client.delete("/cart")
    assert response.status_code == 200
    assert response.json()["ok"] is True

    cart_response = client.get("/cart")
    assert cart_response.json()["items"] == []


def test_checkout_success():
    client.post("/cart/add?pid=0&qty=1")
    client.post("/cart/add?pid=1&qty=2")

    response = client.post("/checkout")
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) == 2

    cart_response = client.get("/cart")
    assert cart_response.json()["items"] == []


def test_checkout_empty_cart():
    response = client.post("/checkout")
    assert response.status_code == 400


def test_orders():
    client.post("/cart/add?pid=0&qty=1")
    client.post("/checkout")

    response = client.get("/orders")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1