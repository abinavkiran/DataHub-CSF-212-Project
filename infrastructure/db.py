import os
import enum
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Integer, BigInteger, Boolean, DateTime, Enum, ForeignKey, Text, JSON, select, literal
from sqlalchemy.orm import sessionmaker, declarative_base, relationship, aliased

# Allow overriding for test suites, default to in-memory SQLite for seamless testing when Docker is down
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///:memory:")

# Initialize explicit engine
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class ObjectType(str, enum.Enum):
    blob = "blob"
    tree = "tree"

class Blob(Base):
    """Immutable data storage points."""
    __tablename__ = "blob"
    blob_hash = Column(String, primary_key=True)
    size_bytes = Column(BigInteger, default=0)
    is_compressed = Column(Boolean, default=False)

class Tree(Base):
    """Represents a directory node."""
    __tablename__ = "tree"
    tree_hash = Column(String, primary_key=True)
    entries = relationship("TreeEntry", back_populates="tree")

class TreeEntry(Base):
    """Maps filenames dynamically to underlying Blobs or sub-Trees."""
    __tablename__ = "tree_entry"
    id = Column(Integer, primary_key=True, autoincrement=True)
    tree_hash = Column(String, ForeignKey("tree.tree_hash"))
    name = Column(String, nullable=False)
    object_hash = Column(String, nullable=False) # Polymorphic: matches blob_hash OR tree_hash
    object_type = Column(Enum(ObjectType), nullable=False)

    tree = relationship("Tree", back_populates="entries")

class Commit(Base):
    """Repo snapshot states creating a directed graph via lineage."""
    __tablename__ = "commit"
    commit_hash = Column(String, primary_key=True)
    # parent_hash points backward to trace chronological history
    parent_hash = Column(String, ForeignKey("commit.commit_hash"), nullable=True) 
    tree_hash = Column(String, ForeignKey("tree.tree_hash"), nullable=False)
    author = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Branch(Base):
    """Human readable pointers marking specific Commits."""
    __tablename__ = "branch"
    name = Column(String, primary_key=True)
    commit_hash = Column(String, ForeignKey("commit.commit_hash"), nullable=False)

class Metadata(Base):
    """Dataset analytics stored persistently regarding a dataset blob or tree."""
    __tablename__ = "metadata"
    id = Column(Integer, primary_key=True, autoincrement=True)
    target_hash = Column(String, nullable=False)
    stats = Column(JSON, nullable=False)

def get_db_session():
    """Yields a SQLAlchemy session to connect to Postgres."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db(test_engine=None):
    """Creates all tables based on declarative base."""
    target_engine = test_engine or engine
    Base.metadata.create_all(bind=target_engine)

# =======================
# Recursive CTE Query API
# =======================

def get_commit_history(session, start_commit_hash: str):
    """
    Returns an ordered list of commits from `start_commit_hash` backward to the root.
    Utilizes a Recursive Database CTE to traverse parent_hash iteratively.
    """
    # Base case: Retrieve all fields from the selected starting commit natively in SQL
    base_q = select(
        Commit.commit_hash, 
        Commit.parent_hash, 
        Commit.author, 
        Commit.message, 
        Commit.created_at, 
        literal(1).label("depth")
    ).where(Commit.commit_hash == start_commit_hash).cte(name="commit_history", recursive=True)

    # Recursive step: Join previous CTE against the Commit table finding the 'parent'
    recursive_q = select(
        Commit.commit_hash, 
        Commit.parent_hash, 
        Commit.author, 
        Commit.message, 
        Commit.created_at, 
        (base_q.c.depth + 1).label("depth")
    ).join(base_q, Commit.commit_hash == base_q.c.parent_hash)

    # Combine Base and Recursion
    history_cte = base_q.union_all(recursive_q)
    
    # Query the resolved CTE ordered chronologically (shallowest/newest first)
    query = select(history_cte).order_by(history_cte.c.depth.asc())
    return session.execute(query).mappings().all()

def get_tree_closure(session, start_tree_hash: str):
    """
    Returns every unique blob_hash referenced deeply inside this Tree or sub-trees.
    Utilizes a Recursive CTE to crawl TreeEntry dynamically inside the DB engine.
    """
    # Base case: the initial folder's raw contents
    base_q = select(
        TreeEntry.tree_hash, 
        TreeEntry.object_hash, 
        TreeEntry.object_type
    ).where(TreeEntry.tree_hash == start_tree_hash).cte(name="tree_closure", recursive=True)

    # Recursive step: Find where inside that folder lies another 'tree' type, and resolve ITS contents
    recursive_q = select(
        TreeEntry.tree_hash, 
        TreeEntry.object_hash, 
        TreeEntry.object_type
    ).join(base_q, TreeEntry.tree_hash == base_q.c.object_hash)\
     .where(base_q.c.object_type == ObjectType.tree)

    closure_cte = base_q.union_all(recursive_q)

    # Filter out sub-folders; isolated data blob hashes are returned 
    query = select(closure_cte.c.object_hash)\
        .where(closure_cte.c.object_type == ObjectType.blob)\
        .distinct()
    
    return session.execute(query).scalars().all()

# =======================
# Branch Pointers Logic
# =======================

def update_branch(session, branch_name: str, target_commit_hash: str):
    """
    Creates or updates a human-readable branch pointer linearly managing the DAG heads.
    """
    branch = session.query(Branch).filter_by(name=branch_name).first()
    if branch:
        branch.commit_hash = target_commit_hash
    else:
        branch = Branch(name=branch_name, commit_hash=target_commit_hash)
        session.add(branch)
    session.commit()
    return branch

def get_branch_history(session, branch_name: str):
    """
    Returns the complete recursive lineage specifically tracing down from a Branch Pointer head.
    """
    branch = session.query(Branch).filter_by(name=branch_name).first()
    if not branch:
        raise ValueError(f"Branch '{branch_name}' does not exist.")
    
    return get_commit_history(session, branch.commit_hash)

