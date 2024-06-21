"""camera_pid controller."""

from controller import Display, Keyboard, Robot, Camera
from vehicle import Car, Driver
import numpy as np
import cv2
from datetime import datetime
import os
import pandas as pd
import time
import threading
#Getting image from camera




def get_image(camera):
    raw_image = camera.getImage()
    image = np.frombuffer(raw_image, np.uint8).reshape(
        (camera.getHeight(), camera.getWidth(), 4)
    )
    return image


#Display image
def display_image(display, image):
    # Image to display
    image_rgb = np.dstack((image, image,image,))
    # Display image
    image_ref = display.imageNew(
        image_rgb.tobytes(),
        Display.RGB,
        width=image_rgb.shape[1],
        height=image_rgb.shape[0],
    )
    display.imagePaste(image_ref, 0, 0, False)

#initial angle and speed
manual_steering = 0
steering_angle = 0
angle = 0.0
speed = 15
continue_capture = True
imagenes_ind = 1

# set target speed
def set_speed(kmh):
    global speed            #robot.step(50)
#update steering angle
def set_steering_angle(wheel_angle):
    global angle, steering_angle
    # Check limits of steering
    if (wheel_angle - steering_angle) > 0.1:
        wheel_angle = steering_angle + 0.1
    if (wheel_angle - steering_angle) < -0.1:
        wheel_angle = steering_angle - 0.1
    steering_angle = wheel_angle

    # limit range of the steering angle
    if wheel_angle > 0.5:
        wheel_angle = 0.5
    elif wheel_angle < -0.5:
        wheel_angle = -0.5
    # update steering angle
    angle = wheel_angle

#validate increment of steering angle
def change_steer_angle(inc):
    global manual_steering
    # Apply increment
    new_manual_steering = manual_steering + inc
    # Validate interval
    if new_manual_steering <= 25.0 and new_manual_steering >= -25.0:
        manual_steering = new_manual_steering
        set_steering_angle(manual_steering * 0.02)
    # Debugging
    if manual_steering == 0:
        print("going straight")
    else:
        turn = "left" if steering_angle < 0 else "right"
        print("turning {} rad {}".format(str(steering_angle),turn))

# main
def main():
    global continue_capture
    # Create the Robot instance.
    robot = Car()
    driver = Driver()

    # Get the time step of the current world.
    timestep = int(robot.getBasicTimeStep())

    # Create camera instance
    camera = robot.getDevice("camera")
    camera.enable(timestep)  # timestep

    # processing display
    display_img = Display("display")

    #create keyboard instance
    keyboard=Keyboard()
    keyboard.enable(timestep)

    imagenes_ent = dict()


    def capture_image(camera):
        global continue_capture,imagenes_ind
        while continue_capture:
            time.sleep(0.5)
            image = get_image(camera)
            display_image(display_img,image)
            current_datetime = str(datetime.now().strftime("%Y-%m-%d %H-%M-%S"))
            img_name = f"{current_datetime}_{imagenes_ind}.png"
            camera.saveImage(os.getcwd() + "/train/" + img_name, 3)
            driver.setSteeringAngle(angle)
            driver.setCruisingSpeed(speed)
            imagenes_ent[img_name] = angle
            imagenes_ind += 1
    t = threading.Thread(target=capture_image,args=(camera,))
    t.start()
    while robot.step() != -1:
        # Get image from camera



        # Process and display image
        # grey_image = greyscale_cv2(image)

        # Transformada de Hough
        # hough_image = hough_transform(grey_image,image)

        #change_steer_angle(rotation_angle)

        #display_image(display_img, grey_image)

        key=keyboard.getKey()
        if key == keyboard.UP: #up
            set_steering_angle(0)
            print("center")
        elif key == keyboard.DOWN: #down
            set_steering_angle(0)
            print("center")
        elif key == keyboard.RIGHT: #right
            change_steer_angle(1)
            print("right")
        elif key == keyboard.LEFT: #left
            change_steer_angle(-1)
            print("left")
        elif key == keyboard.HOME: #Escape
            break
        else:
            pass
            #set_steering_angle(0)

        #update angle and speed


    continue_capture = False
    paths = pd.DataFrame(zip(imagenes_ent.keys(),imagenes_ent.values()),columns=["Paths","Angle"])
    paths.to_csv(os.getcwd() +"/imagenes_entrenamiento.csv")


if __name__ == "__main__":
    main()