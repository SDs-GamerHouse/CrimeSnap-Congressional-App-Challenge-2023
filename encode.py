import cv2
import face_recognition 
import pickle
import os
import firebase_admin 
from firebase_admin import credentials, db, storage

cred = credentials.Certificate("private_database_key.json") # path/to/serviceAccountKey.json
firebase_admin.initialize_app(cred,{
    "databaseURL": "https://crimesnap-8d4d6-default-rtdb.firebaseio.com/",
    "storageBucket": "crimesnap-8d4d6.appspot.com"
})

# Importing test criminal images
images_path = "Test_Images"
images_path_list = os.listdir(images_path)
del images_path_list[0]

# Storing the criminal images and names in a list
images_list = []
criminal_names = []
for path in images_path_list:
    images_list.append(cv2.imread(os.path.join(images_path, path)))
    criminal_names.append(os.path.splitext(path)[0])
    
    # Getting criminal images and uploading to database
    file_name = f"{images_path}/{path}"
    bucket = storage.bucket()
    blob  = bucket.blob(file_name)
    blob.upload_from_filename(file_name)

def find_encodings(img_list):
    encoded_image_list = []

    for image in img_list:
        image = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
        encoded_image = face_recognition.face_encodings(image)[0]
        encoded_image_list.append(encoded_image)
    return encoded_image_list

print("Encoding images......")
encoded = find_encodings(images_list)
encoded_images_with_names = [encoded,criminal_names]
print("Encoding complete")

# Saving encoded images with names into file
print("Saving to file....")
file = open("Encoded.p","wb")
pickle.dump(encoded_images_with_names,file)
file.close()
print("File Saved")