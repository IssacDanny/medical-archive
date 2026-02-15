# utils.py
import os
import io
import functools
from dotenv import load_dotenv
from PIL import Image
from sentence_transformers import SentenceTransformer
import pandas as pd
import pydicom
import numpy as np
from tqdm import tqdm

# 1. CONFIGURATION
# We load the secrets from the .env file immediately.
load_dotenv()

# We use a global variable to cache the AI model.
# This prevents reloading it (which is slow) if we call the function multiple times.
_model = None


def get_connection_uri():
    """
    Retrieves the secure MongoDB connection string from the environment.
    """
    uri = os.getenv("MONGODB_URI")
    if not uri:
        raise ValueError("Critical Error: MONGODB_URI not found in .env file.")
    return uri


def db_mission(phase_name):
    """The Staff: Employs the Foundation to prepare every mission."""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # DEFERRED IMPORT: We import from demo only when the function is called
            # This prevents circular import errors.
            from demo import defining_db

            print(f"\n{'=' * 10} {phase_name.upper()} {'=' * 10}")
            client, db, collection, fs = defining_db()
            try:
                return func(db, collection, fs, *args, **kwargs)
            finally:
                client.close()
                print(f">>> {phase_name} Complete.")

        return wrapper

    return decorator

def get_real_embedding(source):
    """
    The Intelligence Engine.
    Takes an image file path OR a PIL Image object, passes it through the CLIP neural network,
    and returns a vector (a list of floating-point numbers).
    """
    global _model

    # Lazy loading: We only load the heavy model if we actually need it.
    if _model is None:
        print("   [System] Initialising Neural Network (CLIP)... please wait, lady and gentleman.")
        # 'clip-ViT-B-32' is a standard model for matching images and text.
        _model = SentenceTransformer('clip-ViT-B-32')

    try:
        # Check if source is a file path (string) or an image object
        if isinstance(source, str):
            img = Image.open(source)
        else:
            # Assume it's a PIL Image object
            img = source

        # Generate the embedding
        # The model returns a numpy array; MongoDB requires a standard Python list.
        vector = _model.encode(img).tolist()

        return vector
    except Exception as e:
        print(f"   [Error] Failed to process image: {e}")
        return []


def display_image(binary_data, title="Medical Scan"):
    """
    The Visualiser.
    Takes raw binary data (bytes) from GridFS and opens it in a window.
    """
    try:
        # Convert bytes back into an Image object
        image = Image.open(io.BytesIO(binary_data))

        # Show the image (this opens the default OS image viewer)
        image.show(title=title)
        print(f"   [Visual] Displaying image: {title}")
    except Exception as e:
        print(f"   [Error] Could not display image: {e}")


def load_metadata(excel_path):
    """
    Loads radiologist reports from Excel and creates a lookup dictionary.
    """
    if not os.path.exists(excel_path):
        print(f"   [Error] Metadata file not found at {excel_path}")
        return None

    try:
        df = pd.read_excel(excel_path, engine='openpyxl')
    except ImportError as e:
        print(f"   [Error] Missing dependencies: {e}. Please run 'pip install -r requirements.txt'")
        return None

    # Create lookup: {PatientID (str): Notes}
    meta_lookup = {
        str(row['Patient ID']): row["Clinician's Notes"] 
        for index, row in df.iterrows() 
        if pd.notna(row['Patient ID'])
    }
    return meta_lookup


def scan_directory(source_path, meta_lookup):
    """
    Scans the source directory for DICOM files and matches them with metadata.
    """
    if not os.path.isabs(source_path):
        source_path = os.path.abspath(source_path)

    if not os.path.exists(source_path):
        print(f"   [Error] Source path {source_path} does not exist.")
        return []

    print("   [System] Scanning directory structure... this may take a moment.")
    
    dataset = []
    patient_folders = [f for f in os.listdir(source_path) if os.path.isdir(os.path.join(source_path, f))]
    
    print(f"   [System] Found {len(patient_folders)} potential patient folders.")
    
    for p_id_folder in tqdm(patient_folders, desc="Indexing"):
        p_id_int = str(int(p_id_folder)) if p_id_folder.isdigit() else p_id_folder
        
        if p_id_int not in meta_lookup:
            continue
            
        clinician_notes = meta_lookup[p_id_int]
        p_path = os.path.join(source_path, p_id_folder)
        
        for root, dirs, files in os.walk(p_path):
            dicom_files = [f for f in files if f.lower().endswith('.ima') or f.lower().endswith('.dcm')]
            
            if dicom_files:
                dicom_files.sort()
                middle_idx = len(dicom_files) // 2
                target_file = dicom_files[middle_idx]
                full_path = os.path.join(root, target_file)
                scan_type = os.path.basename(root)
                
                dataset.append({
                    "patient_id": f"PAT-{p_id_folder}",
                    "original_id": p_id_int,
                    "name": f"Patient {p_id_int}", # Anonymised
                    "scan_type": scan_type,
                    "notes": clinician_notes,
                    "file_path": full_path
                })
    
    return dataset


def process_dicom_image(file_path):
    """
    Reads a DICOM file, normalizes it, and converts it to a PIL Image and bytes buffer.
    Returns: (image_object, image_bytes)
    """
    try:
        ds = pydicom.dcmread(file_path)
        pixel_array = ds.pixel_array.astype(float)
        
        # Normalize to 0-255
        scaled_image = (np.maximum(pixel_array, 0) / pixel_array.max()) * 255.0
        scaled_image = np.uint8(scaled_image)
        
        image = Image.fromarray(scaled_image)
        
        # Convert to RGB if needed
        if image.mode != "RGB":
            image = image.convert("RGB")
        
        # Create bytes buffer
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)
        
        return image, img_byte_arr
    except Exception as e:
        print(f"   [Error] Processing DICOM {file_path}: {e}")
        return None, None
