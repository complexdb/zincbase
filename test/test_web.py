def test_index(server_and_args):
    app, server, args = server_and_args
    response = app.test_client().get('/')
    assert response.status_code == 200
    data = response.data.decode('utf-8')
    assert '<title>Zincbase Graph Server</title>' in data
    assert 'src="bundle.js"' in data