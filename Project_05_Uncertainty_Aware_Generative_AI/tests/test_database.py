def test_database_api_available():
    import database
    assert callable(database.init_db)
    assert callable(database.save_analysis)
    assert callable(database.get_history)
