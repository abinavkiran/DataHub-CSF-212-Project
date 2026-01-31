# DataHub: Merkle DAG-Backed Content-Addressable Storage for ML Data Lineage

## 1. Executive Summary
DataHub is a distributed version control system (VCS) engineered specifically for high-volume binary datasets and machine learning models. Unlike traditional source control systems (e.g., Git), which degrade in performance with large binary files, DataHub utilizes a **Content-Addressable Storage (CAS)** architecture backed by a relational database. The system provides atomic versioning, automatic data deduplication, and granular lineage tracking for AI/ML workflows via a Python-based Command Line Interface (CLI).

## 2. Problem Statement
In modern data science and machine learning pipelines, the "Reproducibility Crisis" is a significant bottleneck. While code is versioned via Git, the associated datasets (gigabytes in size) and model weights are often managed manually. This leads to:
- **Redundancy**: Massive storage waste due to saving multiple copies of slightly modified datasets.
- **Loss of Lineage**: Inability to mathematically prove which dataset version produced a specific model.
- **Concurrency Issues**: Race conditions when multiple researchers attempt to modify data registries simultaneously.

## 3. System Architecture & Database Logic
The core innovation of DataHub lies in its implementation of a **Merkle Directed Acyclic Graph (DAG)** within a PostgreSQL environment to ensure data integrity and storage efficiency.

### 3.1. The Content-Addressable Storage (CAS) Model
DataHub separates the logical state of a project from its physical storage.
- **Deduplication**: When a file is committed, the system computes its SHA-256 hash. If the hash already exists in the Blobs registry, the physical upload is skipped, and a new pointer is created. This results in $O(1)$ storage cost for duplicate data.
- **Immutable Blob Storage**: Binary objects are stored in a flat file system (or object storage), indexed strictly by their hash. This guarantees that data, once written, can never be silently corrupted.

### 3.2. The Database Schema (DBMS Core)
The relational database acts as the "Index" and "State Manager" for the system. It implements a **Merkle Directed Acyclic Graph (DAG)** to track versioning and data integrity.

#### Core Entities & Attributes

| Entity | Primary Attributes | Description |
| :--- | :--- | :--- |
| **COMMIT** | `commit_hash` (PK), `parent_hash` (FK), `author`, `created_at`, `message` | Represents a specific version/snapshot of the project. Implements a recursive relationship for history. |
| **TREE** | `tree_hash` (PK) | Represents a directory structure. Serves as a root for a specific commit. |
| **TREE_ENTRY** | `id` (PK), `tree_hash` (FK), `name`, `mode`, `object_hash` (FK) | Maps filenames to their physical storage (Blobs) or sub-directories (Trees). |
| **BLOB** | `blob_hash` (PK), `size_bytes`, `storage_path`, `is_compressed` | Stores the actual file content, indexed by its SHA-256 hash for deduplication. |
| **METADATA** | `id` (PK), `target_hash` (FK), `stats` (JSONB) | Stores statistical properties (schemas, row counts, metrics) associated with a commit or file. |

#### Relational Architecture
- **Inverted Indexing**: Files are first hashed into `BLOBs`. `TREE_ENTRY` records then map project-relative paths to these immutable hashes.
- **Recursive DAG**: The `COMMIT` table uses a self-referencing `parent_hash` to reconstruct the timeline of changes.
- **Atomic Snapshots**: A single `commit_hash` points to a root `TREE`, which recursively defines the entire state of the repository at that moment.

- **Commits Table**: Implements a recursive relationship (`ParentHash` FK) to build the version history tree.
- **TreeObjects Table**: Stores directory structures as JSONB objects, mapping file paths to their respective Blob Hashes.
- **Metadata Table**: A queryable index that extracts and stores statistical properties of the data (e.g., row counts, schema definitions, model accuracy metrics) upon commit.

## 4. Functional Modules & Team Division
The development is divided into six distinct backend engineering roles, ensuring parallel execution and structural modularity.

| Module | Scope & Key Deliverables | Team Member |
| :--- | :--- | :--- |
| **Module 1: DAG Architecture & Schema Design** | Implementation of recursive SQL schema (CTEs) to manage commit history and branch pointers. | **Abinav Kiran** (@abinavkiran) |
| **Module 2: Storage Engine & Deduplication** | Development of the hashing engine (SHA-256) and optimized "Put/Get" system to prevent redundant writes. | **Aditya Khemka** (@Aditya-Khemka) |
| **Module 3: Client-Side CLI (Python)** | Development of the user-facing terminal tool (`datahub init`, `push`, `pull`) for file scanning and API communication. | **Kedar Medishetty** (@KedarMedishetty) |
| **Module 4: High-Performance Networking** | Implementation of API Gateway (HTTP/2) handling multipart binary streams and chunked upload protocols. | **Romir Shetty** (@romir3) |
| **Module 5: Metadata Extraction & Indexing** | Automated parsing logic for CSV, JSON, and Parquet files to index statistical metadata upon commit. | **Saurabh Kumar** (@sko2004) |
| **Module 6: Query Language & Reporting** | Domain-specific query parser allowing users to filter data versions via metrics (e.g., `datahub log --metric "accuracy > 0.9"`). | **Pashuvula Niranand Reddy** (@niranand11) |

## 5. Technical Stack
- **Database**: PostgreSQL (utilizing Recursive CTEs and JSONB).
- **Backend**: Go (Golang) or Python (FastAPI) for high-concurrency handling.
- **CLI Client**: Python (Click/Argparse).
- **Protocol**: HTTP/2 for efficient binary streaming.

## 6. Conclusion
DataHub demonstrates advanced proficiency in Database Management Systems by applying complex data structures (Merkle Trees) within a relational model. It solves a critical real-world infrastructure problem, prioritizing data integrity, storage optimization, and system scalability.
