import cv2
import numpy as np

# Load and resize images
image1 = cv2.imread('input/Part_input_image1.jpg')
image2 = cv2.imread('input/Part_input_image2.jpg')

if image1 is None or image2 is None:
    raise ValueError("One or both images could not be loaded. Check file paths.")

# Resize to reduce memory usage
image1 = cv2.resize(image1, (image1.shape[1]//2, image1.shape[0]//2))
image2 = cv2.resize(image2, (image2.shape[1]//2, image2.shape[0]//2))

print("Loaded and resized images")

# Convert images to grayscale
gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)

print("Converted images to grayscale")

# Initialize ORB detector
orb = cv2.ORB_create()

# Detect key points and descriptors
keypoints1, descriptors1 = orb.detectAndCompute(gray1, None)
keypoints2, descriptors2 = orb.detectAndCompute(gray2, None)

if descriptors1 is None or descriptors2 is None:
    raise ValueError("Feature matching failed. No descriptors found.")

print(f"Detected key points: {len(keypoints1)} in image1, {len(keypoints2)} in image2")

# Use BFMatcher to find matches
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
matches = bf.match(descriptors1, descriptors2)

if len(matches) == 0:
    raise ValueError("No matches found between images.")

print(f"Found {len(matches)} matches")

# Sort matches by distance (best matches first)
matches = sorted(matches, key=lambda x: x.distance)[:100]

# Extract matched points
points1 = np.array([keypoints1[m.queryIdx].pt for m in matches], dtype=np.float32)
points2 = np.array([keypoints2[m.trainIdx].pt for m in matches], dtype=np.float32)

print("Extracted matched points")

# Find homography
H, mask = cv2.findHomography(points2, points1, cv2.RANSAC, 5.0)

if H is None:
    raise ValueError("Homography computation failed.")

print("Computed homography matrix")

# Get dimensions for warping
height1, width1 = image1.shape[:2]
height2, width2 = image2.shape[:2]

# Warp image2 onto image1
panorama = cv2.warpPerspective(image2, H, (width1 + width2, max(height1, height2)))
panorama[0:height1, 0:width1] = image1  # Overlay image1 on the panorama

print("Stitched images")

# Convert to grayscale for cropping black areas
gray_panorama = cv2.cvtColor(panorama, cv2.COLOR_BGR2GRAY)
_, thresh = cv2.threshold(gray_panorama, 1, 255, cv2.THRESH_BINARY)
contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

if len(contours) > 0:
    x, y, w, h = cv2.boundingRect(contours[0])
    cropped_panorama = panorama[y:y+h, x:x+w]
    print("Cropped panorama")
else:
    cropped_panorama = panorama  

# Save output
cv2.imwrite('output/panorama.jpg', cropped_panorama)
print("Panorama saved as 'panorama.jpg'")
print("Done")
