import cv2

def detect_face_violations(frame):
    """
    Detect face-related violations for proctoring.
    Returns list of violation messages.
    """
    violations = []
    
    if frame is None:
        violations.append("Invalid frame - Camera issue")
        return violations
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Load Haar Cascade for face detection
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    )
    
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
    
    if len(faces) == 0:
        violations.append('No face detected - Possible looking away or absence')
    elif len(faces) > 1:
        violations.append('Multiple faces detected - Suspicious activity')
    
    return violations