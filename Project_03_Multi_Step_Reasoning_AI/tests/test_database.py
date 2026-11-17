def test_database_module_imports():
    import database
    assert callable(database.initialize_db)
    assert callable(database.save_run)
    assert callable(database.list_runs)
