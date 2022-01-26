# importing the packages
import numpy as np
import argparse
import cv2
from google.colab.patches import cv2_imshow
from PIL import Image
import matplotlib.pyplot as plt
import os
from scipy.spatial import distance as dist

# main class for object detection script
class MobileNetSSD:

    def __init__(self, args, verbose=False):
        '''
        args : parameters send from command line
        verbose : True , if we want to see overall classes predicted
        '''
        self.image = args.image # image path
        self.depth_estimated_image = args.depth_estimated_image # depth estimated image path
        self.prototxt = args.prototxt # file containing info about caffe model
        self.model = args.model # weights of caffe model
        self.confidence = args.confidence # confidence (threshold) value for prediction
        self.query = args.query # query string to return which class
        self.verbose = verbose # verbose to debug
    
    
    # main function 
    def main(self):

        # all CLASSES for which MobileNetSSD was originally pretrained
        CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
        	"bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
        	"dog", "horse", "motorbike", "person", "pottedplant", "sheep",
        	"sofa", "train", "tvmonitor"]

        # storing random colors for bounding boxes ,
        # since image is colored , so all RGB colors assigned
        COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))
        # loading model
        print("loading model...")
        net = cv2.dnn.readNetFromCaffe(self.prototxt, self.model)
        # read image

        image = cv2.imread(self.image)
        depth_estimated_image = cv2.imread(self.depth_estimated_image)
        # finding height, weight
        h, w = image.shape[0], image.shape[1]
        # perform preprocessing like mean subtraction and scaling
        blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 0.007843, (300, 300), 127.5)

        # pass the blob through the network and obtain the detections and
        print("Passing the image to the model...")
        net.setInput(blob)
        detections = net.forward()
        detected = 0
        detected_items = set()
        # now constructing bounding boxes for every object detected
        for i in range(0, detections.shape[2]):
            # for every image detected extract the confidence
            confidence = detections[0, 0, i, 2]
            # only draw bounding box if it is greater than threshold confidence
            if confidence > float(self.confidence):
                # extracting the index of the label
                idx = int(detections[0, 0, i, 1])
                detected_items.add(CLASSES[idx])
                if self.query == CLASSES[idx]:
                    # extracting the four offset values for bounding boxes
                    box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                    # setting the four core coordinates to draw the rectangle
                    (startX, startY, endX, endY) = box.astype("int")
                    label = f"{CLASSES[idx]} : {'%.3f' % round(confidence, 3)}"
                    # increment every time it is detected
                    detected += 1
                    cv2.rectangle(image, (startX, startY), (endX, endY), (0, 255, 0), 2)	
                    
                    cv2.circle(image, (endX, endY), 5, (0, 0, 255), -1)
                    cv2.circle(image, (endX, h), 5, (0, 0, 255), -1)
                    cv2.line(image, (endX, endY), (endX, h), (0, 0, 255), 2)
                    cv2.line(depth_estimated_image, (endX, endY), (endX, h), (0, 0, 255), 2)
                    
                    dist_cal = float(dist.euclidean((endX, endY), (endX, h)) / 12)
#                     mX = (endX + endY) * 0.5
#                     x = mX - 10 if mX - 10 > 10 else mX + 10
#                     cv2.putText(image, "{:.2f} ft".format(dist_cal), (int(x), int((endX + h) * 0.5)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

#                     mY = (endX + h) * 0.5
                    y = endY - 15 if endY - 15 > 15 else endY + 15
                    cv2.putText(image, "{:.2f} ft".format(dist_cal), (int(endX), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                    cv2.putText(depth_estimated_image, "{:.2f} ft".format(dist_cal), (int(endX), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                    
                    cv2.rectangle(depth_estimated_image, (startX, startY), (endX, endY), (0, 255, 0), 2)
                    y = startY - 15 if startY - 15 > 15 else startY + 15
                    cv2.putText(image, label, (startX, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    cv2.putText(depth_estimated_image, label, (startX, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        if not detected:
            print(f"NO {self.query} detected in the given image !")
        else:
            print(f"{self.query} detected {detected} !")
        cv2_imshow(image)
        cv2_imshow(depth_estimated_image)
#         b,g,r = cv2.split(image)
#         image_rgb = cv2.merge((r,g,b))
#         plt.imshow(image_rgb)
#         plt.show()
        cv2.imwrite('/content/Object-Detection/bounding_box_image.jpg', image)
        cv2.imwrite('/content/Object-Detection/depth_bounding_box_image.jpg', depth_estimated_image)
#         cv2.waitKey(0)
        if self.verbose:
            print(f"All objects detected in the image : {detected_items}")


# main driver function
if __name__ == '__main__':
    print("WELCOME TO Object DETECTION")
    parser = argparse.ArgumentParser(description='Automating RoI extraction', epilog='Happy detection :)')
    parser.add_argument('image', type=str, help='Image path')
    parser.add_argument('depth_estimated_image', type=str, help='Depth estimated image path')
    parser.add_argument('prototxt', type=str, help='info about model')
    parser.add_argument('model', type=str, help='model file of caffemodel type')
    parser.add_argument('confidence', type=str, help='threshold confidence %')
    parser.add_argument('query', type=str, help='Query string to search for')
    parser.add_argument('-v', type=str, help='debug output to print all items detected')
    args = parser.parse_args()
    m = MobileNetSSD(args, args.v)
    m.main()
