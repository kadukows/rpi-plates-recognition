def test_init_db_command(runner, monkeypatch):
    class Recorder:
        called = False

    def fake_init_db():
        Recorder.called = True

    monkeypatch.setattr('rpiplatesrecognition.db.init_db', fake_init_db)
    result = runner.invoke(args=['init-db'])
    assert 'Initialized db' in result.output
    assert Recorder.called
