# THE ASCLEPIOS MEDICAL ARCHIVE: OPERATIONAL MANUAL

## 1. The Briefing
This project demonstrates the usage of MongoDB with the usecase of managing a modern medical imaging archive. We move beyond simple text storage to handle Big Data through a stateful, three-phase lifecycle: **Defining** the infrastructure, **Constructing** the archive with real-world imagery, and **Manipulating** the data through advanced Vector Similarity Search.

### The Program constitution:
Our program logic include. 
- **Implemented Logic:** Core DBMS operations (Connections, Indexing, GridFS Vaulting, Aggregation Pipelines). This is the logic which we will implement in the demonstration.
- **Abstracted Logic:** Utility functions (Neural Network Embeddings, UI Rendering, Secure URI handling) housed in `utils.py`.

---

## 2. The Dataset
The archive is built upon a "Big Data" foundation of real-world medical imagery.

-   **Source:** We utilise the **"[Lumbar Spine MRI Dataset](https://data.mendeley.com/datasets/k57fr854j2/2)"**.
-   **Structure:**
    -   **[Metadata](https://data.mendeley.com/datasets/s6bgczr8s2/2):** `data/Radiologists Report.xlsx` contains clinical notes, patient IDs, and diagnosis. 
    -   **Imagery:** `data/raw_images/` contains the raw DICOM files (`.dcm` / `.ima`) organized by patient.
-   **The Link:** You can download the dataset from the links above and organize them in the `data/` folder. The `demo.py` script automatically correlates the clinical notes in the Excel sheet with the binary pixel data in the DICOM files during Phase II ingestion.

---

## 3. Preparation (The Setup)

Before the demonstration commences, the following Groundwork must be completed:

### A. Install Dependency
We utilise **Poetry** to manage our environment. To equip the project with its necessary kit, simply navigate to the project root and execute:

```bash
poetry install
```

This command will read the `pyproject.toml` file, create a dedicated virtual environment, and install the exact versions of `pymongo` and `pillow` required for the mission.

**Option B: Standard Pip**
If you do not use Poetry, you can install the dependencies directly:
```bash
pip install -r requirements.txt
```

### B. The Atlas Cluster
1.  Establish a **MongoDB Atlas** cluster (M0 tier is sufficient).
2.  Get the Atlas Connection String and paste it into the .env file.

---

## 4. The Demonstration

The demonstration is executed in three distinct, stateful missions. Each mission builds upon the state left by the previous one.

### Phase I: DEFINING (The Infrastructure)
**Command:** `poetry run python demo.py 1`
**Alternative:** `python demo.py 1`
- **What to explain:** We are establishing the connection and naming our namespace. We are telling the DBMS how to structure its "Vault" (GridFS) and how to map its "Coordinates" (Vector Index).
- **Visual Confirmation:** The terminal will confirm the connection to the cluster and the definition of the `MedicalArchive` database.

### Phase II: CONSTRUCTING (The Intake)
**Command:** `poetry run python demo.py 2`
**Alternative:** `python demo.py 2`
- **What to explain:** We are ingesting real data. 
    - **Text:** Patient metadata.
    - **Binary:** The MRI image is partitioned and stored in the **GridFS Vault**.
    - **Intelligence:** A real embedding model generates a vector signature.
- **Big Data Note:** Explain that while we process a "Hero" record live, the system is simultaneously acknowledging a pre-existing bulk dataset of 1,000+ records.

### Phase III: MANIPULATING (The Intelligence)
**Command:** `poetry run python demo.py 3`
**Alternative:** `python demo.py 3`
- **What to explain:** The "Payoff." We retrieve data from the stateful archive to satisfy the **3 Hospital Requirements**:
    1.  **Patient History:** Retrieve text and image when given a patient ID.
    2.  **Condition Search:** Retrieve text and image when given a patient ID and conditions (e.g., T2 sagittal MRI).
    3.  **Visual Similarity:** Retrieve MRI images that are similar to one MRI image from a given patient ID.
- **Visual Confirmation:** The terminal will display the retrieved records, and windows will open displaying the MRI scans, proving the DBMS has successfully navigated the multi-dimensional vector space.

## 5. Troubleshooting & Maintenance

- **Duplication:** This demonstration is designed to be run sequentially. If you wish to "Reset" the archive, you must manually clear the `PatientScans` collection and the `fs.files` / `fs.chunks` collections in Atlas or run the **command** `poetry run python demo.py 0` to drop the database.
- **Latency:** The Vector Search Index may take a few moments to "warm up" after the first ingestion of data. If Phase 3 returns no results immediately after Phase 2, allow the system a moment to finish its indexing.
- **The Vault:** Remember that images are not in the document; they are in GridFS. If you delete a document, you must also delete its corresponding file in the vault to maintain a tidy archive.
