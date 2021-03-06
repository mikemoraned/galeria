import math
import numpy as np
import cv2
import sys

max_frames = 10000
detect_frequency = 10
bucket_width = 20

input_filename = sys.argv[1]
output_filename = sys.argv[2]

cap = cv2.VideoCapture(input_filename)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)
out = cv2.VideoWriter(output_filename, -1, fps, (width, height))

# params for ShiTomasi corner detection
feature_params = dict(maxCorners=200,
                      qualityLevel=0.3,
                      minDistance=7,
                      blockSize=7)

# Parameters for lucas kanade optical flow
lk_params = dict(winSize=(15, 15),
                 maxLevel=2,
                 criteria=(
                     cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10,
                     0.03))

# Create some random colors
max_colors = math.ceil(max_frames / detect_frequency) * feature_params[
    "maxCorners"]
color = np.random.randint(0, 255, (max_colors, 3))

# Take first frame and find corners in it
ret, old_frame = cap.read()
old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)
p0 = cv2.goodFeaturesToTrack(old_gray, mask=None, **feature_params)

# Create a mask image for drawing purposes
mask = np.zeros_like(old_frame)

frame_count = 0
ret, frame = cap.read()
while ret and frame_count < max_frames:
    frame_count += 1
    print("Frame: %s" % frame_count)

    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # calculate optical flow
    p1, st, err = cv2.calcOpticalFlowPyrLK(old_gray, frame_gray, p0, None,
                                           **lk_params)

    # Select good points
    good_new = p1[st == 1]
    good_old = p0[st == 1]

    # draw the tracks
    for i, (new, old) in enumerate(zip(good_new, good_old)):
        a, b = new.ravel()
        c, d = old.ravel()
        mask = cv2.line(mask, (a, b), (c, d), color[i].tolist(), 2)
        frame = cv2.circle(frame, (a, b), 5, color[i].tolist(), -1)
    img = cv2.add(frame, mask)

    out.write(img)

    # Now update the previous frame and previous points
    old_gray = frame_gray.copy()
    p0 = good_new.reshape(-1, 1, 2)

    # find new corners
    if frame_count % detect_frequency == 0:
        extra = cv2.goodFeaturesToTrack(frame_gray, mask=None,
                                        **feature_params)
        candidate_p0 = np.concatenate((p0, extra), axis=0)
        bucketed_p0 = (candidate_p0 / bucket_width).round(decimals=0)
        _, indexes = np.unique(bucketed_p0,
                               axis=0,
                               return_index=True)
        print("Update p0: frame %s, total %s " % (frame_count, len(indexes)))
        p0 = candidate_p0[indexes]

    ret, frame = cap.read()

cap.release()
out.release()
