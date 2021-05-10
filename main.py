import os
import sys
import time
import cv2
import face_rec 
from queue import Queue
from threading import Thread

camera = cv2.VideoCapture(0)

def consumer(in_q):
    while True:
        file_name = in_q.get()
        result= face_rec.fdetect(file_name)
        print(result)
        in_q.task_done()

def read_video(q_out):
    num_frames=0
    c_image_path=""
    while True:
        
        if num_frames == 0:
            start = time.time()
        ret, frame = camera.read()
        num_frames=num_frames+1
        if num_frames > 20:
            end = time.time()
            seconds = end - start
            #print ("Time taken : {0} seconds".format(seconds))
            fps  = num_frames / seconds
            print("FPS %.1f" % fps)
            num_frames = 0
            c_image="captured_imgae.jpg"
            c_image_path = os.path.join("cv_img", c_image)
            cv2.imwrite(c_image_path,frame)
            q_out.put(c_image_path)
        
        #time.sleep(0.3)
        #cv2.imshow("Video",frame)
        cv2.waitKey(1)

# Create the shared queue and launch both threads
n = len(sys.argv)
print("Total arguments passed:", n)
 
# Arguments passed
print("\nName of Python script:", sys.argv[0])
if n > 1 :
    face_rec.train_data()

q = Queue()
t1 = Thread(target = consumer, args =(q, ))
t2 = Thread(target = read_video, args =(q, ))
t1.start()
t2.start()
#t2.join()
# Wait for all produced items to be consumed
#q.join()
