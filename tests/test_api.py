def test_take_photo_success(client, monkeypatch):
    class Recorder:
        called = False

    def fake_open():
        Recorder.called = True

    monkeypatch.setattr('rpiplatesrecognition.libs.gate.gate.open', fake_open)

    response = client.get('/api/take_photo')
    j = response.get_json()
    assert j == {'success': True}
    assert Recorder.called

# will be implemented when structure for routine photo -> acquisition ->
# access decision will be finished
def test_take_photo_fail(client, monkeypatch):
    pass
