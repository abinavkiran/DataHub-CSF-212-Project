from query.parser import build_filter, execute_query
from infrastructure.db import Base, engine, SessionLocal, Metadata

def setup_metadata(session):
    # Clear table
    session.query(Metadata).delete()
    session.commit()

    # Insert test data
    m1 = Metadata(target_hash="t1", stats={"accuracy": 0.95, "loss": 0.10})
    m2 = Metadata(target_hash="t2", stats={"accuracy": 0.80, "loss": 0.30})
    m3 = Metadata(target_hash="t3", stats={"accuracy": 0.60, "loss": 0.50})

    session.add_all([m1, m2, m3])
    session.commit()


def test_execute_query_accuracy():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    setup_metadata(session)

    ast = build_filter("accuracy > 0.9")
    results = execute_query(session, ast)

    assert len(results) == 1
    assert results[0][0].target_hash == "t1"

    session.close()


def test_execute_query_loss():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    setup_metadata(session)

    ast = build_filter("loss < 0.2")
    results = execute_query(session, ast)

    assert len(results) == 1
    assert results[0][0].target_hash == "t1"

    session.close()


def test_execute_query_no_result():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    setup_metadata(session)

    ast = build_filter("accuracy > 0.99")
    results = execute_query(session, ast)

    assert len(results) == 0

    session.close()