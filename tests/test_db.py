from rpiplatesrecognition.db import get_db

def test_get_close_db(app):
    with app.app_context():
        db = get_db()
        assert db is get_db()

def test_init_db_command(runner, monkeypatch):
    class Recorder:
        called = False

    def fake_init_db():
        Recorder.called = True

    monkeypatch.setattr('rpiplatesrecognition.db.init_db', fake_init_db)
    result = runner.invoke(args=['init-db'])
    assert 'Initialized db' in result.output
    assert Recorder.called
