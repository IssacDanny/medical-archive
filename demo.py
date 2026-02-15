# demo.py
import sys
import os
from pymongo import MongoClient
import gridfs
from utils import (
    db_mission, get_real_embedding, display_image, get_connection_uri,
    load_metadata, scan_directory, process_dicom_image
)
import pandas as pd
import pydicom
import numpy as np
from tqdm import tqdm
from PIL import Image
import io


# ==========================================
# PHASE I: DEFINING
# ==========================================
def defining_db():
    """
    The Storehouse & Surveyor: Connects to Atlas and ensures
    the 'PatientScans' collection exists (Idempotent).
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
    
    return client, db, collection, fs


def define_vector_index(collection):
    """Mission 1.1: Define the mathematical map."""
    index_model = {
        "name": "vector_index",
        "definition": {"mappings": {"dynamic": True, "fields": {
            "image_vector": {"dimensions": 512, "similarity": "cosine", "type": "knnVector"}
        }}}
    }
    try:
        # Note: create_search_index is available in pymongo>=4.7
        collection.create_search_index(model=index_model)
        print("   [DBMS] Vector Search Index defined.")
    except Exception as e:
        print(f"   [Info] Index status: {e}")


@db_mission("Phase I: Defining")
def phase_1_defining(db, collection, fs):
    # We show that the components are already initialised by the decorator
    print(f"   [Setup] Connection: {db.client.address}")
    define_vector_index(collection)


# ==========================================
# PHASE II: CONSTRUCTING
# ==========================================

def insert_patient_record(collection, fs, p_id, name, s_type, img_path):
    """Mission 2.1: Atomic intake logic for a single record."""
    if collection.count_documents({"patient_id": p_id, "scan_type": s_type}) > 0:
        print(f"   [Skip] {p_id} ({s_type}) already exists.")
        return

    print(f"   [Intake] Processing {p_id} - {s_type}...")
    vector = get_real_embedding(img_path)
    
    # Store image in GridFS
    with open(img_path, "rb") as f:
        f_id = fs.put(f, filename=f"{p_id}_{s_type}.jpg")

    doc = {
        "patient_id": p_id, "name": name, "scan_type": s_type,
        "image_file_id": f_id, "image_vector": vector
    }
    collection.insert_one(doc)
    print(f"   [Success] {s_type} archived.")



def ingest_big_data_archive(collection, fs, source_path):
    """
    Interface for big data ingestion using Dataframe and DICOM.
    Structure: source_path/PatientID/ExamID/ScanType/Image.ima
    """
    print(f"\n   [Bulk] Initiating Big Data Protocol for source: '{source_path}'")
    
    # 1. Load Metadata
    excel_path = os.path.join("data", "Radiologists Report.xlsx")
    meta_lookup = load_metadata(excel_path)
    if not meta_lookup:
        return
    print(f"   [Metadata] Loaded {len(meta_lookup)} patient records.")

    # 2. Index Directory
    dataset = scan_directory(source_path, meta_lookup)
    if not dataset:
        return
    print(f"   [System] Indexed {len(dataset)} valid scans ready for ingestion.")
    
    # LIMIT FOR TESTING
    dataset = dataset[:400]
    print(f"   [Test Mode] Limiting ingestion to {len(dataset)} records.")
    
    # 3. Filter Duplicates
    # Check which records already exist to avoid unnecessary processing
    print("   [System] Checking for existing records...")
    patient_ids = list(set(d['patient_id'] for d in dataset))
    # Fetch all records for these patients to check scan types
    existing_cursor = collection.find(
        {"patient_id": {"$in": patient_ids}},
        {"patient_id": 1, "scan_type": 1, "_id": 0}
    )
    existing_keys = set((d['patient_id'], d['scan_type']) for d in existing_cursor)
    
    new_records = [
        r for r in dataset 
        if (r['patient_id'], r['scan_type']) not in existing_keys
    ]
    
    if not new_records:
        print("   [Info] All records already exist. Nothing to ingest.")
        return

    print(f"   [System] Processing {len(new_records)} new records...")

    # 4. Ingest Loop
    batch_docs = []
    success_count = 0
    
    for record in tqdm(new_records, desc="Ingesting"):
        try:
            # Process DICOM
            image, img_byte_arr = process_dicom_image(record['file_path'])
            if image is None:
                continue

            # Generate Embedding
            vector = get_real_embedding(image)
            
            # Upload to GridFS
            f_id = fs.put(img_byte_arr, filename=f"{record['patient_id']}_{record['scan_type']}.jpg")
            
            # Prepare Document
            doc = {
                "patient_id": record['patient_id'],
                "name": record['name'],
                "scan_type": record['scan_type'],
                "clinician_notes": record['notes'],
                "image_file_id": f_id,
                "image_vector": vector,
                "dicom_source": record['file_path']
            }
            batch_docs.append(doc)
            success_count += 1
            
        except Exception as e:
            print(f"   [Error] Failed in {record['patient_id']}: {e}")
            pass
    
    if batch_docs:
        try:
            collection.insert_many(batch_docs)
            print(f"   [Success] Bulk write completed. Ingested {len(batch_docs)} records.")
        except Exception as e:
            print(f"   [Error] Bulk insert failed: {e}")
    else:
        print("   [Info] No valid documents to insert.")


@db_mission("Phase II: Constructing")
def phase_2_constructing(db, collection, fs):
    # 1. The Hero Record (Live Implementation)
    hero_img = os.path.join("images", "hero_scan.jpg")
    
    # Check if hero image exists
    if not os.path.exists(hero_img):
        print(f"   [Error] Hero image not found at {hero_img}")
        return

    insert_patient_record(collection, fs, "PAT-007", "James Bond", "T2 Sagittal MRI", hero_img)
    # Re-using the same image for demonstration purposes, though conceptually it's a different scan type
    insert_patient_record(collection, fs, "PAT-007", "James Bond", "T1 Axial MRI", hero_img)

    # 2. The Big Data Archive (Placeholder Interface)
    ingest_big_data_archive(collection, fs, "data/raw_images/01_MRI_Data")


# ==========================================
# PHASE III: MANIPULATING
# ==========================================

def mission_retrieve_id(collection, p_id):
    print(f"\n--- Mission 3.1: ID Search ({p_id}) ---")
    results = list(collection.find({"patient_id": p_id}))
    count = len(results)
    print(f"   [DBMS] Found {count} records for this patient.")

    for i, doc in enumerate(results):
        print(f"   [{i+1}] Scan: {doc.get('scan_type', 'Unknown')} | Note: {str(doc.get('clinician_notes', 'N/A'))[:50]}...")
    return results


def mission_retrieve_condition(collection, fs, p_id, s_type):
    print(f"\n--- Mission 3.2: Condition Search ({s_type}) ---")
    record = collection.find_one({"patient_id": p_id, "scan_type": s_type})
    if record:
        print(f"   [Success] Specific scan retrieved.")
        grid_out = fs.get(record['image_file_id'])
        display_image(grid_out.read(), title=s_type)
    else:
        print(f"   [Falied] No record found for {p_id} - {s_type}")
    return record


def mission_vector_search(collection, anchor_record):
    print(f"\n--- Mission 3.3: Similarity Search ---")

    if not anchor_record or 'image_vector' not in anchor_record:
        print("   [Error] Anchor record is invalid or missing vector data.")
        return

    pipeline = [
        {"$vectorSearch": {
            "index": "vector_index",
            "path": "image_vector",
            "queryVector": anchor_record['image_vector'],
            "numCandidates": 10,
            "limit": 2
        }},
        {"$project": {
            "_id": 0,
            "patient_id": 1,
            "scan_type": 1,
            "score": {"$meta": "vectorSearchScore"}
        }}
    ]

    print("   [DBMS] Executing Aggregation Pipeline...")
    results = list(collection.aggregate(pipeline))

    if not results:
        print("   [Warning] No similar scans found. The Vector Index may still be initialising on Atlas.")
    else:
        for doc in results:
            print(f"   [Match] ID: {doc['patient_id']} ({doc.get('scan_type', 'Unknown')}) | Similarity: {doc['score']:.4f}")


@db_mission("Phase III: Manipulating")
def phase_3_manipulating(db, collection, fs):
    p_id = "PAT-0001"
    s_type = "T2_TSE_SAG_384_0002"

    print("\n" + "="*40)
    print("MEDICAL ARCHIVE")
    print("="*40)

    # 1. [Req 1] Retrieve text & image by Patient ID
    print(f"\n[Req 1] Retrieve all records for {p_id}...")
    mission_retrieve_id(collection, p_id)

    # 2. [Req 2] Retrieve by ID + Condition (Scan Type)
    print(f"\n[Req 2] Retrieve specific scan: {p_id} + {s_type}...")
    anchor = mission_retrieve_condition(collection, fs, p_id, s_type)

    # 3. [Req 3] Retrieve Similar Images (Vector Search)
    if anchor:
        print(f"\n[Req 3] Finding similar images to {p_id}'s {s_type}...")
        mission_vector_search(collection, anchor)
    else:
        print("   [Error] Anchor record not found for vector search.")


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
