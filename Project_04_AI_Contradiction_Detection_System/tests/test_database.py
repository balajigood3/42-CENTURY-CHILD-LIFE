def test_database_functions_import():
    import database
    assert callable(database.init_db) and callable(database.save_result) and callable(database.get_history)
