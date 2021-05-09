import os
import time
import os.path
import math
import cv2
import face_recognition
import pickle
#import eel
from sklearn import neighbors
#from base64 import b64encode
from PIL import Image, ImageDraw,ImageFont
from face_recognition.face_recognition_cli import image_files_in_folder
#from gtts import gTTS
from queue import Queue
from datetime import datetime
import csv_update

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
TRAINDATA = "Data_Base"
#camera = cv2.VideoCapture(0)

def train(train_dir, model_save_path=None, n_neighbors=None, knn_algo='ball_tree', verbose=False):

    X = []
    y = []

    # Loop through each person in the training set
    for class_dir in os.listdir(train_dir):
        if not os.path.isdir(os.path.join(train_dir, class_dir)):
            continue

        # Loop through each training image for the current person
        for img_path in image_files_in_folder(os.path.join(train_dir, class_dir)):
            image = face_recognition.load_image_file(img_path)
            face_bounding_boxes = face_recognition.face_locations(image)

            if len(face_bounding_boxes) != 1:
                # If there are no people (or too many people) in a training image, skip the image.
                if verbose:
                    print("Image {} not suitable for training: {}".format(img_path, "Didn't find a face" if len(face_bounding_boxes) < 1 else "Found more than one face"))
            else:
                # Add face encoding for current image to the training set
                X.append(face_recognition.face_encodings(image, known_face_locations=face_bounding_boxes)[0])
                y.append(class_dir)

    # Determine how many neighbors to use for weighting in the KNN classifier
    if n_neighbors is None:
        n_neighbors = int(round(math.sqrt(len(X))))
        if verbose:
            print("Chose n_neighbors automatically:", n_neighbors)

    # Create and train the KNN classifier
    knn_clf = neighbors.KNeighborsClassifier(n_neighbors=n_neighbors, algorithm=knn_algo, weights='distance')
    knn_clf.fit(X, y)

    # Save the trained KNN classifier
    if model_save_path is not None:
        with open(model_save_path, 'wb') as f:
            pickle.dump(knn_clf, f)

    return knn_clf

def predict(X_img_path, knn_clf=None, model_path=None, distance_threshold=0.6):

    if not os.path.isfile(X_img_path) or os.path.splitext(X_img_path)[1][1:] not in ALLOWED_EXTENSIONS:
        raise Exception("Invalid image path: {}".format(X_img_path))

    if knn_clf is None and model_path is None:
        raise Exception("Must supply knn classifier either thourgh knn_clf or model_path")

    # Load a trained KNN model (if one was passed in)
    if knn_clf is None:
        with open(model_path, 'rb') as f:
            knn_clf = pickle.load(f)

    # Load image file and find face locations
    X_img = face_recognition.load_image_file(X_img_path)
    X_face_locations = face_recognition.face_locations(X_img)

    # If no faces are found in the image, return an empty result.
    if len(X_face_locations) == 0:
        return []

    # Find encodings for faces in the test iamge
    faces_encodings = face_recognition.face_encodings(X_img, known_face_locations=X_face_locations)

    # Use the KNN model to find the best matches for the test face
    closest_distances = knn_clf.kneighbors(faces_encodings, n_neighbors=1)
    are_matches = [closest_distances[0][i][0] <= distance_threshold for i in range(len(X_face_locations))]

    # Predict classes and remove classifications that aren't within the threshold
    return [(pred, loc) if rec else ("unknown", loc) for pred, loc, rec in zip(knn_clf.predict(faces_encodings), X_face_locations, are_matches)]

def show_prediction_labels_on_image(img_path, predictions):
    pil_image = Image.open(img_path).convert("RGB")
    draw = ImageDraw.Draw(pil_image)

    for name, (top, right, bottom, left) in predictions:
        # Draw a box around the face using the Pillow module
        draw.rectangle(((left, top), (right, bottom)), outline=(0, 0, 255))

        # There's a bug in Pillow where it blows up with non-UTF-8 text
        # when using the default bitmap font
        name = name.encode("UTF-8")

        # Draw a label with a name below the face
        
        text_width, text_height = draw.textsize(name)
        draw.rectangle(((left, bottom - text_height - 10), (right, bottom)), fill=(0, 0, 255), outline=(0, 0, 255))
        draw.text((left + 6, bottom - text_height - 5), name, fill=(255, 255, 255, 255))

    # Remove the drawing library from memory as per the Pillow docs
    del draw

    # Display the resulting image
    pil_image.show()

def to_bytes(bytes_or_str):
    if isinstance(bytes_or_str, str):
        value = bytes_or_str.encode() # uses 'utf-8' for encoding
    else:
        value = bytes_or_str
    return value # Instance of bytes
    
def to_str(bytes_or_str):
    if isinstance(bytes_or_str, bytes):
        value = bytes_or_str.decode() # uses 'utf-8' for encoding
    else:
        value = bytes_or_str
    return value # Instance of str

def train_data():
    start = time.time()
    print("Training KNN classifier...")
    classifier = train(TRAINDATA, model_save_path="trained_knn_model.clf", n_neighbors=2)
    done = time.time()
    elapsed = done - start
    print("Time Taken: %0.2f Sec" % elapsed)
    print("Training complete!")
    
def fdetect(c_image_path):
    found_list = ["False"]
    face_dected=False
    pname="Unknown"
    o_image="procesed_image.png"
    s_image="send_image.png"
    #print ("Detecting Face")    

    o_image_path = os.path.join("cv_img", o_image)
    s_image_path = os.path.join("cv_img", s_image)

    #predictions = predict(c_image_path, model_path="/home/pi/Project/trained_knn_model.clf")
    start = time.time()
    predictions = predict(c_image_path, model_path="trained_knn_model.clf")
    end = time.time()
    seconds = end - start
    #ty_res = time.gmtime(seconds)
    #res = time.strftime("%H:%M:%S",ty_res)
    #print(res)
    #print ("Detecting Face Time taken : {0} seconds".format(seconds))
    frame = cv2.imread(c_image_path)
    now = datetime.now()
    
    t1 = now.strftime("%H:%M:%S")
    d1 = now.strftime("%d/%m/%Y")
    
    for name, (top, right, bottom, left) in predictions:
        #print("- {} {}--> Found {} at ({}, {})".format(d1,t1,name, left, top))
        found1 = [d1,t1,name]
        found_list[0]="True"
        found_list.append(found1)
        csv_update.update(name,d1,t1)
        pname=name
        face_dected=True
        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (255, 0,0), 2)      
        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, top-35), (right-20, top), (255, 0,0), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX         
        cv2.putText(frame, name, (left, top - 6), font, 1.0, (255, 255, 255), 2,1)
        img=frame
        sub_face = img[top-100:bottom+100, left-100:right+100]
        if(sub_face is not None):
            cv2.imwrite(s_image_path,sub_face)

    cv2.imwrite(o_image_path,frame)
    return found_list


