import uuid
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def create_unique_username():
    return f"testuser_{uuid.uuid4().hex[:8]}"


def test_health_check():
    response = client.get('/api/auth/health')
    assert response.status_code == 200
    assert response.json().get('status') == 'ok'


def test_register_and_login():
    username = create_unique_username()
    password = 'Password123!'
    response = client.post('/api/auth/register', json={
        'username': username,
        'password': password,
        'email': f'{username}@example.com'
    })
    assert response.status_code == 200
    assert response.json().get('success') is True

    response = client.post('/api/auth/login', json={
        'username': username,
        'password': password
    })
    assert response.status_code == 200
    body = response.json()
    assert 'access_token' in body
    assert body.get('token_type') == 'bearer'


def test_create_product_and_list():
    username = create_unique_username()
    password = 'Password123!'
    client.post('/api/auth/register', json={
        'username': username,
        'password': password,
        'email': f'{username}@example.com'
    })
    response = client.post('/api/auth/login', json={
        'username': username,
        'password': password
    })
    token = response.json().get('access_token')
    headers = {'Authorization': f'Bearer {token}'}

    product_payload = {
        'name': 'Producto de prueba',
        'price': 250.0,
        'tax_rate': 0.12
    }
    response = client.post('/api/products', json=product_payload, headers=headers)
    assert response.status_code == 200
    assert response.json().get('success') is True
    assert response.json().get('product_id') is not None

    response = client.get('/api/products', headers=headers)
    assert response.status_code == 200
    products = response.json().get('products')
    assert isinstance(products, list)
    assert any(item['name'] == 'Producto de prueba' for item in products)


def test_create_invoice():
    username = create_unique_username()
    password = 'Password123!'
    client.post('/api/auth/register', json={
        'username': username,
        'password': password,
        'email': f'{username}@example.com'
    })
    response = client.post('/api/auth/login', json={
        'username': username,
        'password': password
    })
    token = response.json().get('access_token')
    headers = {'Authorization': f'Bearer {token}'}

    invoice_payload = {
        'invoice_number': '001-001-' + str(uuid.uuid4().int)[:9]
    }
    response = client.post('/api/invoices', json=invoice_payload, headers=headers)
    assert response.status_code == 200
    assert response.json().get('success') is True
    assert response.json().get('invoice_id') is not None
