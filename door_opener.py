import face_recognition as fr
import cv2
import RPi.GPIO as GPIO
from datetime import datetime, timedelta
import numpy as np 
import platform 
import pickle

auth_face_encodings = []
auth_face_metadata = []

def button1_init():
    # Input pin is 15
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(15, GPIO.IN)
    
def button1():
    # Input pin is 15
    for i in range(10):
        x = GPIO.input(15)
        if(x == 0):
            return True
    return False

def random_rgb():
    color = list(np.random.choice(range(256), size=3))
    return color

def save_auth_faces():
    with open("auth_faces.dat", "wb") as fd_file:
        face_data = [auth_face_encodings, auth_face_metadata]
        pickle.dump(face_data, fd_file)
        print("Authorized faces backed up to the disk.")
        
def load_auth_faces():
    try:
        with open("auth_faces.dat", "rb") as fd_file:
            auth_face_encodings, auth_face_metadata = pickle.load(fd_file)
            print("Authorized faces loaded from disk.")
    except FileNotFoundError as e:
        print("No previous authoirzed faces found.")
        pass
    
      
def register_authorized_face(face_encoding, image):
    auth_face_encodings.append(face_encoding)
    
    auth_face_metadata.append({"first_seen": datetime.now(),
                               "first_seen_this_interaction": datetime.now(),
                               "last_seen": datetime.now(),
                               "number_of_times_seen": 1,
                               "number_of_frames_seen:" 1,
                               "image_of_face:", image})
    
def is_authorized(face_encoding):
    
    if len(auth_face_encodings) == 0:
        return None
    
    distances = fr.face_distance(auth_face_encodings, face_encoding)
    
    best_match_index = np.argmin(distances)
    
    metadata = None
    
    if distances[best_match_index] < 0.65:
        metadata = auth_face_metadata[best_match_index]
        metadata["last_seen"] = datetime.now()
        metadata["seen_frames"] += 1
        
        if timedelta(minutes=5) - metadata["first_seen_this_interaction"] < 0:
            metadata["first_seen_this_interaction"] = datetime.now()
            metadata["number_of_times_seen"] += 1
        
        return metadata
    
    
def main():
    vid_cap = cv2.VideoCapture(0)
    
    while True:
        # Get frame of Vid Capture
        ret, frame = vid_cap.read()

        # Resize frame to quarter of the size
        quarter_frame = cv2.resize(frame, (0,0), fx=0.25, fy=0.25)

        # Convert the image from BGR color to RGB color
        rgb_quarter_frame = quarter_frame[:, :, ::-1]
    
        locations = fr.face_locations(rgb_quarter_frame)
        
        encodings = fr.face_encodings(rgb_quarter_frame, locations)
        
        for locations, encoding in zip(locations, encodings):
            
            metadata = is_authorized(encoding)
            
            if metadata != None:
                
                # Must move motor and allow user into the house
                
                labels.append("Authorized")
                
            else:
                
                labels.append("Unauthorized")
                
                # Check if button GPIO port is true
                if(button1()):
                
                    # If true then save the face
                    top, right, bottom, left = location
                    image = rgb_quarter_frame[top:bottom, left:right]
                    image = cv2.resize(image, (150, 150))

                    register_authorized_face(encoding, image)
            
        for (top, right, bottom, left), label in zip(locations, labels):
            
            # Scale up image
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4
            
            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), random_rgb(), 2)
            
            # Draw a label with the description below the face
            cv2.rectangle(frame, (left, bottom -35), (right, bottom), random_rgb, cv2.FILLED)
            
            cv2.putText(frame, label, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)
        
        cv2.imshow('Video', frame)
        
        # Check if button GPIO port is true and then quit with: break
    
        if len(locations) > 0 and frames_since_save > 100:
            save_auth_faces()
            frames_since_save = 0
        else:
            frames_since_save += 1
           
            
    video_capture.release()
    cv2.destroyAllWindows()
    GPIO.cleanup()
        
if __name__ == "__main__":
    button1_init()
    load_auth_faces()
    main()