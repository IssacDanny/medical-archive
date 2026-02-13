# demo.py
import sys
import os
from pymongo import MongoClient
import gridfs
from utils import db_mission, get_real_embedding, display_image, get_connection_uri

# ==========================================
# PHASE I: DEFINING
# ==========================================
def defining_db():
    """
    The Storehouse & Surveyor: Connects to Atlas and ensures
    the 'PatientScans' collection exists (Idempotent).
    """
    # TODO: implement the logic for setting up the database
    # Example:
    """
    client = MongoClient(get_connection_uri())
    # defining db
    db = client['MedicalArchive']

    if "PatientScans" not in db.list_collection_names():
        # defining namespace(record)
        db.create_collection("PatientScans")
        print(f"   [System] Namespace '{db.name}.PatientScans' established.")

    collection = db['PatientScans']
    fs = gridfs.GridFS(db)
    """
    # We must return these variable for it is used by the decorator in the subsequnce implementation
    # return client, db, collection, fs

def define_vector_index(collection):
    """Mission 1.1: Define the mathematical map."""
    # TODO: implement the logic for defining vector index
    # Example:
    """
    index_model = {
        "name": "vector_index",
        "definition": {"mappings": {"dynamic": True, "fields": {
            "image_vector": {"dimensions": 512, "similarity": "cosine", "type": "knnVector"}
        }}}
    }
    try:
        collection.create_search_index(model=index_model)
        print("   [DBMS] Vector Search Index defined.")
    except Exception as e:
        print(f"   [Info] Index status: {e}")
    """


@db_mission("Phase I: Defining")
def phase_1_defining(db, collection, fs):
    # We show that the components are already initialised by the decorator
    # print(f"   [Setup] Connection: {db.client.address}")
    # define_vector_index(collection)
    pass


# ==========================================
# PHASE II: CONSTRUCTING
# ==========================================

def insert_patient_record(collection, fs, p_id, name, s_type, img_path):
    """Mission 2.1: Atomic intake logic for a single record."""
    # TODO: implement the logic for inserting patient record
    # Example:
    """
        if collection.count_documents({"patient_id": p_id, "scan_type": s_type}) > 0:
        print(f"   [Skip] {p_id} ({s_type}) already exists.")
        return

    print(f"   [Intake] Processing {p_id} - {s_type}...")
    vector = get_real_embedding(img_path)
    with open(img_path, "rb") as f:
        f_id = fs.put(f, filename=f"{p_id}_{s_type}.jpg")

    doc = {
        "patient_id": p_id, "name": name, "scan_type": s_type,
        "image_file_id": f_id, "image_vector": vector
    }
    collection.insert_one(doc)
    print(f"   [Success] {s_type} archived.")
    """


def ingest_big_data_archive(collection, fs, source_path):
    """
    Interface for big data ingestion.
    """
    # TODO: implement the logic for big data injestion
    # Example:
    print(f"\n   [Bulk] Initiating Big Data Protocol for source: '{source_path}'")

    # Placeholder Implementation for Demonstration
    print("   [System] Scanning directory for high-resolution medical imagery...")
    print("   [System] 1,240 files detected. Commencing batch processing...")

    # Simulating the workflow steps
    print("   [AI] Batch 1/10: Generating neural embeddings (CLIP-ViT-B-32)...")
    print("   [Vault] Batch 1/10: Partitioning binary data into GridFS chunks...")
    print("   [DBMS] Batch 1/10: Metadata and vectors successfully synchronised.")

    print("   [Bulk] ... (Simulating remaining batches) ...")

    print("   [Success] Big Data Archive successfully integrated into the state.")


@db_mission("Phase II: Constructing")
def phase_2_constructing(db, collection, fs):
    # 1. The Hero Record (Live Implementation)
    #hero_img = os.path.join("images", "hero_scan.jpg")
    # insert_patient_record(collection, fs, "PAT-007", "James Bond", "T2 Sagittal MRI", hero_img)
    # insert_patient_record(collection, fs, "PAT-007", "James Bond", "T1 Axial MRI", hero_img)

    # 2. The Big Data Archive (Placeholder Interface)
    # ingest_big_data_archive(collection, fs, "data/radiology_archive_v4/")
    pass

# ==========================================
# PHASE III: MANIPULATING
# ==========================================

def mission_retrieve_id(collection, p_id):
    # TODO: implement the logic for retrieving patient based on id
    # Example:
    """
    print(f"\n--- Mission 3.1: ID Search ({p_id}) ---")
    count = collection.count_documents({"patient_id": p_id})
    print(f"   [DBMS] Found {count} records for this patient.")
    """

def mission_retrieve_condition(collection, fs, p_id, s_type):
    # TODO: implement the logic for conditional retrieving of patient
    # Example:
    """
    print(f"\n--- Mission 3.2: Condition Search ({s_type}) ---")
    record = collection.find_one({"patient_id": p_id, "scan_type": s_type})
    if record:
        print(f"   [Success] Specific scan retrieved.")
        display_image(fs.get(record['image_file_id']).read(), title=s_type)
    return record
    """


def mission_vector_search(collection, anchor_record):
    # TODO: implement the logic for searching similar mri.
    # Example:
    """
    print(f"\n--- Mission 3.3: Similarity Search ---")

    pipeline = [
        {"$vectorSearch": {
            "index": "vector_index",
            "path": "image_vector",
            "queryVector": anchor_record['image_vector'],
            "numCandidates": 10,
            "limit": 2
        }},
        {"$project": {
            "patient_id": 1,
            "score": {"$meta": "vectorSearchScore"}
        }}
    ]

    print("   [DBMS] Executing Aggregation Pipeline...")
    results = list(collection.aggregate(pipeline))

    if not results:
        print("   [Warning] No similar scans found. The Vector Index may still be initialising on Atlas.")
    else:
        for doc in results:
            print(f"   [Match] ID: {doc['patient_id']} | Similarity: {doc['score']:.4f}")
    """

@db_mission("Phase III: Manipulating")
def phase_3_manipulating(db, collection, fs):
    # p_id, s_type = "PAT-007", "T2 Sagittal MRI"
    # mission_retrieve_id(collection, p_id)
    # anchor = mission_retrieve_condition(collection, fs, p_id, s_type)
    # if anchor:
        #mission_vector_search(collection, anchor)
    pass


# ==========================================
# MAIN EXECUTION
# ==========================================

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python demo.py [0|1|2|3]")
    else:
        choice = sys.argv[1]
        if choice == "1":
            phase_1_defining()
        elif choice == "2":
            phase_2_constructing()
        elif choice == "3":
            phase_3_manipulating()
        elif choice == "0":
            client = MongoClient(get_connection_uri())
            client.drop_database('MedicalArchive')
            print("Clean slate achieved.")