import cv2

image=cv2.imread("Tropical beach  wallpaper desktop laptop background 4k HD 1080p Blue Ocean Palm tree travel images.jpeg")

cv2.namedWindow('Loaded Image', cv2.WINDOW_NORMAL)

cv2.resizeWindow('Loaded Image', 800, 500)

cv2.imshow('Loaded Image', image)
cv2.waitKey(0)
cv2.destroyAllWindows()

print(f"Image Dimensions : {image.shape}")