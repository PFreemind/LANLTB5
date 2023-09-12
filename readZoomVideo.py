import cv2
import matplotlib.pyplot as plot
import pytesseract
import numpy as np

# import the necessary packages
import numpy as np
import cv2
def order_points(pts):
    # initialzie a list of coordinates that will be ordered
    # such that the first entry in the list is the top-left,
    # the second entry is the top-right, the third is the
    # bottom-right, and the fourth is the bottom-left
    rect = np.zeros((4, 2), dtype = "float32")
    # the top-left point will have the smallest sum, whereas
    # the bottom-right point will have the largest sum
    s = pts.sum(axis = 1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    # now, compute the difference between the points, the
    # top-right point will have the smallest difference,
    # whereas the bottom-left will have the largest difference
    diff = np.diff(pts, axis = 1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    # return the ordered coordinates
    return rect
#for image rotation
def four_point_transform(image, pts):
    # obtain a consistent order of the points and unpack them
    # individually
    rect = order_points(pts)
    (tl, tr, br, bl) = rect
    # compute the width of the new image, which will be the
    # maximum distance between bottom-right and bottom-left
    # x-coordiates or the top-right and top-left x-coordinates
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))
    # compute the height of the new image, which will be the
    # maximum distance between the top-right and bottom-right
    # y-coordinates or the top-left and bottom-left y-coordinates
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))
    # now that we have the dimensions of the new image, construct
    # the set of destination points to obtain a "birds eye view",
    # (i.e. top-down view) of the image, again specifying points
    # in the top-left, top-right, bottom-right, and bottom-left
    # order
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype = "float32")
    # compute the perspective transform matrix and then apply it
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
    # return the warped image
    return warped

# Path to the Tesseract OCR executable (change this to match your installation)
#pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract.exe'

# Define the coordinates of the ROI (top-left and bottom-right)
roi_x1, roi_y1, roi_x2, roi_y2 = 0,0,4000,4000#1000, 500, 2400, 1400  # Adjust these coordinates as needed

# Initialize the video capture object
video_path = 'test.mp4'
video_capture = cv2.VideoCapture(video_path)  # Replace 'video.mp4' with your video file path
skip_start_time = 2475  # 1 hour = 3600 seconds
# Initialize the video capture object
video_capture = cv2.VideoCapture(video_path)

# Get the frame rate of the video
frame_rate = int(video_capture.get(cv2.CAP_PROP_FPS))

# Calculate the frame index to start from
start_frame = int(skip_start_time * frame_rate)

# Set the frame index to the calculated starting frame
video_capture.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

while True:
    # Read a frame from the video
    ret, frame = video_capture.read()

    # Check if we have reached the end of the video
    if not ret:
        break
    #image pre-processing
    # Extract the ROI from the frame
    roi_frame = frame[roi_y1:roi_y2, roi_x1:roi_x2]
    
    # Convert the ROI to grayscale for better OCR accuracy
    gray_roi = cv2.cvtColor(roi_frame, cv2.COLOR_BGR2GRAY)
    # ret,thresh = cv2.threshold(gray_roi,70,255,0)
    rect = np.zeros((4, 2), dtype = "float32")
    rect = np.array([[24,230], [1253,50], [1227,449], [11,569] ])
    warped = four_point_transform(gray_roi, rect)
    #could add noise reduction with fastNlMeansDenoisingColored ()
    #also, smarter edge detection?
   # foo,binary=cv2.threshold(warped, 160, 255, cv2.THRESH_BINARY)
    binary = cv2.adaptiveThreshold(warped,255,cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY,151,2)
#    cv2.imshow('foo',binary)
    #plot.imshow(gray_roi)
    # Use Tesseract OCR to extract text from the ROI
   # extracted_text = pytesseract.image_to_string(gray_roi)
    config = ' --psm 7 -c tessedit_char_whitelist=0123456789'
    extracted_text = pytesseract.image_to_string(binary, config=config)

    # You can add additional processing here to filter and extract numbers from 'extracted_text'

    # Display the extracted text on the frame
   # cv2.putText(binary, extracted_text, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
 #   foo,gray_roi=cv2.threshold(roi_frame, 127, 255, cv2.THRESH_BINARY)
    # Display the frame with extracted text
    #cv2.accumulateWeighted(dst, binary, 0.1)
    h=binary.shape[0]
    w=binary.shape[1]
    dst=np.zeros([h, w], dtype=np.uint8)
    '''
    alpha =0.2
    for i in range(h):
        for j in range(w):
            dst[i,j] = dst[i,j] * (1-alpha) + binary[i,j] * (alpha)
    '''
    foo,out=cv2.threshold(binary, 1, 255, cv2.THRESH_BINARY)
   # out= cv2.adaptiveThreshold(dst,160,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,11,2)
    #dst = dst*(1-alpha) + binary*alpha
    extracted_text = pytesseract.image_to_string(out, config=config)
    cv2.putText(out, extracted_text, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow('Frame', out)
    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
    ##hmmmm
    #break image into 4 parts, check each letter individually
    #can write something specific for 7-segment letters
    #calculate mean in 7 roi, get pieces, match to mapping
    #id bad matches
    #1 =[0,1,1,0,0,0,0]
    #2=[1,1,0,1,1,0,1]
    #3=[1,1,1,1,0,0,1]
    #etc
    #really, same as the easrlier comment... removing short contours would help tho
    # can parse for numbers via contours
    #then check each number with nasty 7-segment explicit defintions. that's a decent amount of development...
    
    #well fuck, this just doesn't work
 

# Release the video capture object and close all OpenCV windows
video_capture.release()
cv2.destroyAllWindows()

