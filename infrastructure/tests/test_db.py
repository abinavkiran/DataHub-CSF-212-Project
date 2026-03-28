import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from infrastructure.db import Base, Commit, Tree, TreeEntry, ObjectType, Branch, Blob, Metadata, get_commit_history, get_tree_closure

@pytest.fixture
def session():
    """Setup an isolated, in-memory SQLite database enabling standalone CTE Testing."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.rollback() # Rollback standardizes
    session.close()

def test_commit_history_recursive_cte(session):
    """Verifies chronological backwards traversal of parent Commits returning absolute length and correct depth fields."""
    
    # Base requirements
    t = Tree(tree_hash="tree0")
    session.add(t)
    
    # Setup a chronological chain of 3 commits: c1 <- c2 <- c3
    c1 = Commit(commit_hash="hash1", tree_hash="tree0", author="Creator", message="Init")
    c2 = Commit(commit_hash="hash2", parent_hash="hash1", tree_hash="tree0", author="Creator", message="Update")
    c3 = Commit(commit_hash="hash3", parent_hash="hash2", tree_hash="tree0", author="Partner", message="Fix")
    
    # Link pointing branch
    b = Branch(name="main", commit_hash="hash3")
    
    session.add_all([c1, c2, c3, b])
    session.commit()

    # Fire CTE backwards linearly through parent_hash starting from tail (c3)
    history = get_commit_history(session, "hash3")
    
    assert len(history) == 3
    # Ordered chronologically by ascending depth (1=newest, 3=genesis root)
    assert history[0]["commit_hash"] == "hash3"
    assert history[0]["depth"] == 1
    assert history[1]["commit_hash"] == "hash2"
    assert history[1]["depth"] == 2
    assert history[2]["commit_hash"] == "hash1"
    assert history[2]["depth"] == 3

def test_tree_closure_recursive_cte(session):
    """Verifies that flat and nested directory pointers properly drill downward strictly yielding scalar Blobs (Files)."""
    
    # Setup a nested structure: Root Tree -> [Blob 1, (SubTree -> [Blob 2])]
    
    # 1. Establish Hash mappings natively
    t_root = Tree(tree_hash="root_tree")
    t_sub = Tree(tree_hash="sub_tree")
    
    b1 = Blob(blob_hash="blob_1", size_bytes=100)
    b2 = Blob(blob_hash="blob_2", size_bytes=50)
    
    session.add_all([t_root, t_sub, b1, b2])
    
    # 2. Map their logical connections using polymorphic typing
    root_file_entry = TreeEntry(tree_hash="root_tree", name="file1.txt", object_hash="blob_1", object_type=ObjectType.blob)
    root_folder_entry = TreeEntry(tree_hash="root_tree", name="folder", object_hash="sub_tree", object_type=ObjectType.tree)
    
    sub_file_entry = TreeEntry(tree_hash="sub_tree", name="file2.txt", object_hash="blob_2", object_type=ObjectType.blob)
    
    session.add_all([root_file_entry, root_folder_entry, sub_file_entry])
    session.commit()
    
    # 3. Request the closure computation strictly grabbing leaves inside `root_tree`
    closure_blobs = get_tree_closure(session, "root_tree")
    
    assert len(closure_blobs) == 2
    assert "blob_1" in closure_blobs
    assert "blob_2" in closure_blobs

def test_branch_management(session):
    """Verifies that Branch pointers correctly manipulate the DAG heads and properly bridge CTE retrievals."""
    from infrastructure.db import update_branch, get_branch_history
    
    # Setup base topological map
    t = Tree(tree_hash="tree-branch")
    c1 = Commit(commit_hash="hash-branch-1", tree_hash="tree-branch", author="Test", message="Init")
    session.add_all([t, c1])
    session.commit()
    
    # 1. Create a raw new branch pointer
    branch = update_branch(session, "experiment-1", "hash-branch-1")
    assert branch.name == "experiment-1"
    assert branch.commit_hash == "hash-branch-1"
    
    # 2. Extract entire historical CTE lineage directly through the pointer
    history = get_branch_history(session, "experiment-1")
    assert len(history) == 1
    assert history[0]["commit_hash"] == "hash-branch-1"
    
    # 3. Update pointer mapping iteratively (Fast-Forward simulation)
    c2 = Commit(commit_hash="hash-branch-2", parent_hash="hash-branch-1", tree_hash="tree-branch", author="Test", message="Update")
    session.add(c2)
    session.commit()
    
    update_branch(session, "experiment-1", "hash-branch-2")
    history_new = get_branch_history(session, "experiment-1")
    assert len(history_new) == 2
    assert history_new[0]["commit_hash"] == "hash-branch-2"

    # 4. Rigorous verification rejecting blind traversals
    with pytest.raises(ValueError):
        get_branch_history(session, "non_existent_branch_fatal_error")
