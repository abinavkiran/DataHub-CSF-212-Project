import hashlib
import json

def get_tree_hash(file_map):
    tree_string = json.dumps(file_map, sort_keys=True)
    return hashlib.sha256(tree_string.encode()).hexdigest()

def get_commit_hash(tree_hash):
    return hashlib.sha256(tree_hash.encode()).hexdigest()