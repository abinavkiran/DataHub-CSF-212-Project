from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
import os

# Import contracts from Module 1 (Database) and Module 2 (Storage)
from infrastructure.db import SessionLocal, Commit, Tree, TreeEntry, ObjectType, Metadata, Branch, update_branch, get_branch_history, init_db
from storage.engine import put_blob, BLOB_DIR
from metadata.extractor import extract_metrics
from query.parser import build_filter, execute_query
import mimetypes

# Initialize database schemas
init_db()

app = FastAPI(title="DataHub Node API")

# Dependency to get DB session
def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/check_hash/{blob_hash}")
async def check_hash(blob_hash: str):
    """Checks whether a blob already exists to avoid redundant uploads from CLI."""
    blob_path = os.path.join(BLOB_DIR, blob_hash)
    return {"exists": os.path.exists(blob_path)}

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
    entries = payload.get("entries", payload.get("tree_entries", []))
    
    if not commit_hash or not tree_hash:
        raise HTTPException(status_code=400, detail="commit_hash and tree_hash are required")
        
    # Check if the commit already exists
    existing_commit = session.query(Commit).filter(Commit.commit_hash == commit_hash).first()
    if existing_commit:
        update_branch(session, "main", commit_hash)
        # We don't rollback but commit the branch update
        session.commit()
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

    # Create optional tree entries if provided by the push lifecycle payload
    for entry in entries:
        name = entry.get("name")
        object_hash = entry.get("object_hash")
        object_type_raw = entry.get("object_type")

        if not name or not object_hash or not object_type_raw:
            raise HTTPException(status_code=400, detail="Each tree entry requires name, object_hash, and object_type")

        try:
            object_type = ObjectType(object_type_raw)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=f"Invalid object_type: {object_type_raw}") from exc

        session.add(
            TreeEntry(
                tree_hash=tree_hash,
                name=name,
                object_hash=object_hash,
                object_type=object_type
            )
        )

        if object_type == ObjectType.blob:
            existing_meta = session.query(Metadata).filter_by(target_hash=object_hash).first()
            if not existing_meta:
                mime_type, _ = mimetypes.guess_type(name)
                mime_type = mime_type or "application/octet-stream"
                blob_path = os.path.join(BLOB_DIR, object_hash)
                metrics = extract_metrics(blob_path, mime_type)
                session.add(Metadata(target_hash=object_hash, stats=metrics))
    
    # Push commit before updating branch to satisfy foreign key
    session.flush()

    # Update branch pointer
    update_branch(session, "main", commit_hash)

    try:
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
        
    return {"status": "success", "commit_hash": commit_hash}

@app.get("/log")
async def get_log(session: Session = Depends(get_db_session)):
    try:
        history = get_branch_history(session, "main")
        return {"history": [{"commit_hash": r.commit_hash, "author": r.author, "message": r.message, "created_at": r.created_at} for r in history]}
    except ValueError:
        return {"history": []}

@app.post("/query/")
async def query_metadata(payload: dict, session: Session = Depends(get_db_session)):
    query_string = payload.get("query")
    if not query_string:
         raise HTTPException(status_code=400, detail="Query string is required")
    try:
        ast = build_filter(query_string)
        results = execute_query(session, ast)
        return {"results": [{"target_hash": r[0].target_hash, "stats": r[0].stats} for r in results]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

