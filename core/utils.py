import face_recognition
import os

# We set this to True so the Django views enable the upload features
INSIGHTFACE_AVAILABLE = True 

def compare_faces(known_image_path, unknown_image_path):
    """
    Compares two images and returns True if they match.
    """
    try:
        # Load the image files
        known_image = face_recognition.load_image_file(known_image_path)
        unknown_image = face_recognition.load_image_file(unknown_image_path)

        # Get the face encodings
        known_encodings = face_recognition.face_encodings(known_image)
        unknown_encodings = face_recognition.face_encodings(unknown_image)

        if len(known_encodings) > 0 and len(unknown_encodings) > 0:
            # results is a list of True/False
            results = face_recognition.compare_faces([known_encodings[0]], unknown_encodings[0], tolerance=0.6)
            return results[0]
        
        return False
    except Exception as e:
        print(f"Error during face comparison: {e}")
        return False