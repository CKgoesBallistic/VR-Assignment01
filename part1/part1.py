import cv2
import numpy as np
import matplotlib.pyplot as plt
import random
import os

def preprocess_image(image_path):
    """Preprocesses the image by converting to grayscale and applying Gaussian blur."""
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    return image, gray, blur

def detect_and_segment_coins(image, blur, min_area=1200, output_dir="output/segmented_coins"):
    """Detects coins, segments them as circular images, and saves them."""
    
    # Apply edge detection and dilation
    canny = cv2.Canny(blur, 20, 150)
    dilated = cv2.dilate(canny, None, iterations=2)  # First dilation step
    contours, _ = cv2.findContours(dilated.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filter small contours based on area
    filtered_contours = [c for c in contours if cv2.contourArea(c) >= min_area]
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    segmented = image.copy()
    num_coins = len(filtered_contours)

    for idx, contour in enumerate(filtered_contours):
        (x, y), radius = cv2.minEnclosingCircle(contour)  # Fit minimum enclosing circle
        center = (int(x), int(y))
        radius = int(radius)

        # Draw thicker circle edges
        color = [random.randint(0, 255) for _ in range(3)]
        cv2.circle(segmented, center, radius, color, thickness=5)  # Increased thickness
        cv2.putText(segmented, str(idx+1), (center[0]-10, center[1]+10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # Extract circular ROI
        mask = np.zeros_like(image, dtype=np.uint8)
        cv2.circle(mask, center, radius, (255, 255, 255), thickness=-1)
        coin = cv2.bitwise_and(image, mask)

        # Crop the bounding square around the circle
        x1, y1, x2, y2 = center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius
        circular_coin = coin[y1:y2, x1:x2]

        # Save as PNG with transparency
        alpha = np.zeros_like(mask[:, :, 0])
        cv2.circle(alpha, center, radius, 255, thickness=-1)
        circular_coin = cv2.merge([circular_coin[:, :, 0], circular_coin[:, :, 1], circular_coin[:, :, 2], alpha[y1:y2, x1:x2]])

        coin_filename = os.path.join(output_dir, f"coin_{idx+1}.png")
        cv2.imwrite(coin_filename, circular_coin)
        print(f"Saved circular segmented coin: {coin_filename}")

    print(f"Final Coin Count: {num_coins}")

    return segmented, num_coins

def main(image_path):
    """Main function to process image and visualize the results."""
    image, gray, blur = preprocess_image(image_path)
    
    segmented, num_coins = detect_and_segment_coins(image, blur)

    plt.figure(figsize=(12,6))
    
    plt.subplot(1,2,1)
    plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    plt.title('Original Image')
    plt.axis('off')
    
    plt.subplot(1,2,2)
    plt.imshow(cv2.cvtColor(segmented, cv2.COLOR_BGR2RGB))
    plt.title(f'Segmented Coins ({num_coins} detected)')
    plt.axis('off')
    
    plt.show()

# Run the function with the input image
image_path = "input/input_image_2.jpg"
main(image_path)
