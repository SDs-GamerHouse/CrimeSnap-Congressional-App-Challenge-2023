# Importing required libraries 
import cv2
import os
import pickle
import face_recognition 
import numpy as np
import firebase_admin 
from firebase_admin import credentials, db, storage
from datetime import datetime

cred = credentials.Certificate("private_database_key.json") # path/to/serviceAccountKey.json
firebase_admin.initialize_app(cred,{
    "databaseURL": "https://crimesnap-8d4d6-default-rtdb.firebaseio.com/",
    "storageBucket": "crimesnap-8d4d6.appspot.com"
})

# Setting up the webcam dimensions
cam = cv2.VideoCapture(0)
cam.set(3, 850) # 850 is the width
cam.set(4, 625) # 625 is the height

# Getting the bakcground image for the UI
background_image = cv2.imread("Assets/Background.png")

# Storing mode (Camer Active, alredy recorded, recorded) images in a list
modes_path = "Assets/Modes"
modes_path_list = os.listdir(modes_path)
modes_image_list = []
for path in modes_path_list:
    modes_image_list.append(cv2.imread(os.path.join(modes_path,path)))


mode = 2 # 2-3-1-4 --> cycles through all the mode screens
counter = 0 # Determines when the mode changes
bucket = storage.bucket()

# Bringing in the encoded data file
print("Loading encoded data")
file = open("Encoded.p","rb")
encoded_images_with_names = pickle.load(file)
encoded, criminal_names = encoded_images_with_names
file.close()
print("Encoded data loaded")

# Setting up the UI
while True:
    success, img = cam.read()
    
    if success:
        image = cv2.resize(img, (850, 625)) # 850,625

    # Resizing image to reduce the amount of computing power required
    small_image = cv2.resize(image, (0, 0),None,0.25,0.25)
    small_image = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)

    face_in_current_frame = face_recognition.face_locations(small_image)
    encoded_image_in_current_frame = face_recognition.face_encodings(small_image,face_in_current_frame)

    # Placing the webcam on the background image
    background_image[375:375 + 625, 125:125 + 850] = image

    # Placing the mode screens on the background image
    w,h,_ = modes_image_list[mode].shape
    background_image[300:300 + w, 1275:1275 + h] = modes_image_list[mode]

    if face_in_current_frame:
        for encoded_face,face_location in zip(encoded_image_in_current_frame,face_in_current_frame):
            matches = face_recognition.compare_faces(encoded,encoded_face) 
            face_distance = face_recognition.face_distance(encoded,encoded_face) # Lower the value, the higher the match
            match_index = np.argmin(face_distance)

            if matches[match_index]:
                # Getting data from database
                id = criminal_names[match_index]
                blob = bucket.get_blob(f"Test_Images/{id}.png")
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                criminal_cover_pic = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)

                # Getting the reference to the database
                reference = db.reference(f"Criminals/{id}")

                if counter == 0:
                    counter = 1 
                    mode = 3

                if counter != 0:
                    if counter == 1:
                        criminal_info = db.reference(f"Criminals/{id}").get()
                        # print(f"Criminal Info: {criminal_info}")

                        # Updating num_of_times_spotted on database and UI
                        date_and_time = datetime.strptime(criminal_info["last_spotted_on"],"%m/%d/%Y %H:%M:%S")
                        seconds_elapsed = (datetime.now() - date_and_time).total_seconds()
                        if seconds_elapsed > 15:
                            criminal_info["num_of_times_spotted"]+=1
                            reference.child("num_of_times_spotted").set(criminal_info["num_of_times_spotted"])
                            reference.child("last_spotted_on").set(datetime.now().strftime("%m/%d/%Y %H:%M:%S"))
                        else:
                            mode = 4
                            counter = 0
                            w,h,_ = modes_image_list[mode].shape
                            background_image[300:300 + w, 1275:1275 + h] = modes_image_list[mode]

                    if mode != 4:
                        if 10 < counter < 20:
                            mode = 1

                            # Updating the UI to show the updated mode screen
                            w,h,_ = modes_image_list[mode].shape
                            background_image[300:300 + w, 1275:1275 + h] = modes_image_list[mode]

                        if counter <= 10:
                            cv2.putText(background_image, str(criminal_info["num_of_times_spotted"]),(1310,390),cv2.FONT_HERSHEY_COMPLEX,3,(0,0,0),5)
                            if criminal_info["suspect"] == "Joker":
                                cv2.putText(background_image, str(criminal_info["suspect"]),(1500,775),cv2.FONT_HERSHEY_COMPLEX,0.9,(0,0,0),2)
                                cv2.putText(background_image, str(criminal_info["crime"]),(1360,900),cv2.FONT_HERSHEY_COMPLEX,1,(0,0,0),2)
                            elif criminal_info["suspect"] == "Kylo Ren":
                                cv2.putText(background_image, str(criminal_info["suspect"]),(1450,775),cv2.FONT_HERSHEY_COMPLEX,0.9,(0,0,0),2)
                                cv2.putText(background_image, str(criminal_info["crime"]),(1375,900),cv2.FONT_HERSHEY_COMPLEX,1,(0,0,0),2)
                            elif criminal_info["suspect"] == "Loki":
                                cv2.putText(background_image, str(criminal_info["suspect"]),(1500,775),cv2.FONT_HERSHEY_COMPLEX,0.9,(0,0,0),2)
                                cv2.putText(background_image, str(criminal_info["crime"]),(1450,900),cv2.FONT_HERSHEY_COMPLEX,1,(0,0,0),2)
                            else:
                                cv2.putText(background_image, str(criminal_info["suspect"]),(1400,775),cv2.FONT_HERSHEY_COMPLEX,0.9,(0,0,0),2)
                                cv2.putText(background_image, str(criminal_info["crime"]),(1375,900),cv2.FONT_HERSHEY_COMPLEX,1,(0,0,0),2)

                            background_image[400:400+216, 1475:1475+216] = criminal_cover_pic

                        counter += 1

                        if counter >= 20:
                            counter = 0
                            mode = 2
                            criminal_info = []
                            criminal_cover_pic = []
                            w,h,_ = modes_image_list[mode].shape
                            background_image[300:300 + w, 1275:1275 + h] = modes_image_list[mode]
    else:
        mode = 2
        counter = 0

    cv2.imshow("CrimiFace", background_image)
    cv2.waitKey(1)