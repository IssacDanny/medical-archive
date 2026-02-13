# utils.py
import os
import io
import functools
from dotenv import load_dotenv
from PIL import Image
from sentence_transformers import SentenceTransformer

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

def get_real_embedding(image_path):
    """
    The Intelligence Engine.
    Takes an image file path, passes it through the CLIP neural network,
    and returns a vector (a list of floating-point numbers).
    """
    global _model

    # Lazy loading: We only load the heavy model if we actually need it.
    if _model is None:
        print("   [System] Initialising Neural Network (CLIP)... please wait, lady and gentleman.")
        # 'clip-ViT-B-32' is a standard model for matching images and text.
        _model = SentenceTransformer('clip-ViT-B-32')

    try:
        # Open the image file
        img = Image.open(image_path)

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