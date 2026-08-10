import cv2
import numpy as np
def apply_color_filter(image, filter_type):
    filtered_image=image.copy()
    if filter_type=="red_tint":
        filtered_image[:, :, 1]=0
        filtered_image[:, :, 0]=0

    elif filter_type=="blue_tint":
        filtered_image[:, :, 1]=0
        filtered_image[:, :, 2]=0

    elif filter_type=="green_tint":
            filtered_image[:, :, 0]=0
            filtered_image[:, :, 2]=0

    elif filter_type=="increase_red":
            filtered_image[:, :, 2]=cv2.add(filtered_image[:, :, 0], 50)

    elif filter_type=="decrease_red":
                filtered_image[:, :, 0]=cv2.subtract(filtered_image[:, :, 0], 50)
    return filtered_image

image_path="g"
image=cv2.imread(image_path)

if image_path is None:
       print("Image not Found!")
else:
    filter_type="original"

    print("Press the Following keys to apply filters: ")
    print("1 - Red Tint")
    print("2 - Blue Tint")
    print("3 - Green Tint")
    print("4 - Increase Red Intensity")
    print("5 - decrease Blue Intensity")
    print("6 - Quit")

    while True:
          filtered_image=apply_color_filter(image, filter_type)
          cv2.imshow("Filtered Image", filtered_image)
          key=cv2.waitKey(0)&0xFF

          if key==ord('1'):
                filter_type="red_tint"
          elif key==ord('2'):
                filter_type="blue_tint"
          elif key==ord('3'):
                          filter_type="green_tint"
          elif key==ord('4'):
                          filter_type="increase_red"
          elif key==ord('5'):
                          filter_type="decrease_red"
          elif key==ord('6'):
                  print("Exiting....")
                  break
          else:
                  print("Invalid Key! Please Enter 'r', 'b', 'g', 'i', 'd', or 'q'")

cv2.destroyAllWindows()