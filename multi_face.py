import asyncio
import io
import glob
import os
import string
import sys
import time
import uuid
import requests
from urllib.parse import urlparse
from io import BytesIO
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.face.models import TrainingStatusType, Person, SnapshotObjectType, OperationStatusType
from PIL import Image, ImageDraw

#add environment varible here
KEY = os.environ['FACE_SUBSCRIPTION_KEY']
ENDPOINT = os.environ['FACE_ENDPOINT']
face_client = FaceClient(ENDPOINT, CognitiveServicesCredentials(KEY))

# Detect a face in an image that contains a single face
single_face_image_url = 'https://www.biography.com/.image/t_share/MTQ1MzAyNzYzOTgxNTE0NTEz/john-f-kennedy---mini-biography.jpg'
single_image_name = os.path.basename(single_face_image_url)
detected_faces = face_client.face.detect_with_url(url=single_face_image_url)
if not detected_faces:
    raise Exception('No face detected from image {}'.format(single_image_name))

# Display the detected face ID in the first single-face image.
# Face IDs are used for comparison to faces (their IDs) detected in other images.
print('Detected face ID from', single_image_name, ':')
for face in detected_faces: print (face.face_id)
print()

# Save this ID for use in Find Similar
first_image_face_ID = detected_faces[0].face_id

multi_face_image_url = "http://www.historyplace.com/kennedy/president-family-portrait-closeup.jpg"
multi_image_name = os.path.basename(multi_face_image_url)
detected_faces2 = face_client.face.detect_with_url(url=multi_face_image_url)

# Search through faces detected in group image for the single face from first image.
# First, create a list of the face IDs found in the second image.
second_image_face_IDs = list(map(lambda x: x.face_id, detected_faces2))
# Next, find similar face IDs like the one detected in the first image.
similar_faces = face_client.face.find_similar(face_id=first_image_face_ID, face_ids=second_image_face_IDs)

if not similar_faces[0]:
    print('No similar faces found in', multi_image_name, '.')
    # Print the details of the similar faces detected
else:
    print('Similar faces found in', multi_image_name + ':')
    for face in similar_faces:
            first_image_face_ID = face.face_id
            # The similar face IDs of the single face image and the group image do not need to match,
            # they are only used for identification purposes in each image.
            # The similar faces are matched using the Cognitive Services algorithm in find_similar().
            face_info = next(x for x in detected_faces2 if x.face_id == first_image_face_ID)
            if face_info:
                    print('  Face ID: ', first_image_face_ID)
                    print('  Face rectangle:')
                    print('    Left: ', str(face_info.face_rectangle.left))
                    print('    Top: ', str(face_info.face_rectangle.top))
                    print('    Width: ', str(face_info.face_rectangle.width))
                    print('    Height: ', str(face_info.face_rectangle.height))
