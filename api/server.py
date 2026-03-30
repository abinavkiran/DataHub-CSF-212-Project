from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
import os

# Import contracts from Module 1 (Database) and Module 2 (Storage)
from infrastructure.db import SessionLocal, Commit, Tree, TreeEntry, ObjectType
from storage.engine import put_blob

app = FastAPI(title="DataHub Node API")

# Dependency to get DB session
def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/blobs/")
async def upload_blob(file: UploadFile = File(...)):
    """
    Routes Python's UploadFile StreamingBody straight into the put_blob logic
    without stopping in RAM. Returns the inserted hash locally.
    """
    # Specifically passing the low-level spooling file object to avoid loading into RAM
    hash_str = put_blob(file.file)
    return {"blob_hash": hash_str}

@app.post("/commit/")
async def create_commit(payload: dict, session: Session = Depends(get_db_session)):
    """
    Accepts rigid Tree Entry JSON payloads representing the newest snapshot.
    Leverages Abinav's Schema directly injecting Commits logically.
    """
    commit_hash = payload.get("commit_hash")
    tree_hash = payload.get("tree_hash")
    parent_hash = payload.get("parent_hash")
    author = payload.get("author", "unknown")
    message = payload.get("message", "")
    
    if not commit_hash or not tree_hash:
        raise HTTPException(status_code=400, detail="commit_hash and tree_hash are required")
        
    # Check if the commit already exists
    existing_commit = session.query(Commit).filter(Commit.commit_hash == commit_hash).first()
    if existing_commit:
        return {"status": "success", "commit_hash": commit_hash, "message": "Commit already exists"}

    # Create the top-level tree if it doesn't already exist
    existing_tree = session.query(Tree).filter(Tree.tree_hash == tree_hash).first()
    if not existing_tree:
        new_tree = Tree(tree_hash=tree_hash)
        session.add(new_tree)
        session.flush() # Ensure tree is created before commit
        
    # Create the commit record
    new_commit = Commit(
        commit_hash=commit_hash,
        tree_hash=tree_hash,
        parent_hash=parent_hash,
        author=author,
        message=message
    )
    
    session.add(new_commit)
    
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
        
    return {"status": "success", "commit_hash": commit_hash}
