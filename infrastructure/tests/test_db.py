from infrastructure.db import get_db_session

def test_db_session_yields():
    # Simple test to verify the session function setup works
    session_gen = get_db_session()
    session = next(session_gen)
    assert session is not None
    session.close()
