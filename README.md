# THE ASCLEPIOS MEDICAL ARCHIVE: OPERATIONAL MANUAL

## 1. The Briefing
This project demonstrates the robust capabilities of MongoDB in managing a modern medical imaging archive. We move beyond simple text storage to handle "Big Data" through a stateful, three-phase lifecycle: **Defining** the infrastructure, **Constructing** the archive with real-world imagery, and **Manipulating** the data through advanced Vector Similarity Search.

### The Engineering Philosophy
We employ **Step-Wise Refinement**. 
- **Implemented Logic:** Core DBMS operations (Connections, Indexing, GridFS Vaulting, Aggregation Pipelines).
- **Abstracted Logic:** Utility functions (Neural Network Embeddings, UI Rendering, Secure URI handling) housed in `utils.py`.

---

## 2. Preparation (The Setup)

Before the demonstration commences, the following "Groundwork" must be completed:

### A. Dependency Management
We utilise **Poetry** to manage our environment with precision. To equip the project with its necessary kit, simply navigate to the project root and execute:

```bash
poetry install
```

This command will read the `pyproject.toml` file, create a dedicated virtual environment, and install the exact versions of `pymongo` and `pillow` required for the mission.

### B. The Atlas Cluster
1.  Establish a **MongoDB Atlas** cluster (M0 tier is sufficient).
2.  In `utils.py`, ensure the `get_connection_uri()` function returns your specific Atlas Connection String.
3.  **The Vector Map:** You must define the Vector Search Index in the Atlas UI before Phase 3.
    - **Collection:** `MedicalArchive.PatientScans`
    - **Index Name:** `vector_index`
    - **Field:** `image_vector`
    - **Dimensions:** [Match your real model's output, e.g., 512]
    - **Similarity:** `cosine`

---

## 3. The Demonstration

The demonstration is executed in three distinct, stateful missions. Each mission builds upon the state left by the previous one.

### Phase I: DEFINING (The Infrastructure)
**Command:** `poetry run python demo.py 1`
- **What to explain:** We are establishing the connection and naming our namespace. We are telling the DBMS how to structure its "Vault" (GridFS) and how to map its "Coordinates" (Vector Index).
- **Visual Confirmation:** The terminal will confirm the connection to the cluster and the definition of the `MedicalArchive` database.

### Phase II: CONSTRUCTING (The Intake)
**Command:** `poetry run python demo.py 2`
- **What to explain:** We are ingesting real data. 
    - **Text:** Patient metadata.
    - **Binary:** The MRI image is partitioned and stored in the **GridFS Vault**.
    - **Intelligence:** A real embedding model generates a vector signature.
- **Big Data Note:** Explain that while we process a "Hero" record live, the system is simultaneously acknowledging a pre-existing bulk dataset of 1,000+ records.

### Phase III: MANIPULATING (The Intelligence)
**Command:** `poetry run python demo.py 3`
- **What to explain:** The "Payoff." We retrieve data from the stateful archive.
    - **Mission A:** Retrieve by ID. Show the text and the image extracted from GridFS.
    - **Mission B:** The Similarity Search. We use the `$vectorSearch` pipeline to find images that "look like" our target scan.
- **Visual Confirmation:** Windows will open displaying the retrieved MRI scans, proving the DBMS has successfully navigated the multi-dimensional vector space.

## 4. Troubleshooting & Maintenance

- **Duplication:** This demonstration is designed to be run sequentially. If you wish to "Reset" the archive, you must manually clear the `PatientScans` collection and the `fs.files` / `fs.chunks` collections in Atlas or run the **command** `poetry run python demo.py 0` to drop the database.
- **Latency:** The Vector Search Index may take a few moments to "warm up" after the first ingestion of data. If Phase 3 returns no results immediately after Phase 2, allow the system a moment to finish its indexing.
- **The Vault:** Remember that images are not in the document; they are in GridFS. If you delete a document, you must also delete its corresponding file in the vault to maintain a tidy archive.

***