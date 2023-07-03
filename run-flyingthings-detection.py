#!/usr/bin/python

import os
import sys
import requests
import json
import urllib3
import RPi.GPIO as GPIO
import time
import pygame

# Disable SSL certificate verification warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Set the GPIO mode and specify the LED pins
GPIO.setmode(GPIO.BCM)
led_pin1 = 4
led_pin2 = 5

# Set up the LED pins as outputs
GPIO.setup(led_pin1, GPIO.OUT)
GPIO.setup(led_pin2, GPIO.OUT)

def upload_image(image_path, endpoint_url):
    # Set the headers for the request
    headers = {
        'accept': 'application/json',
    }

    # Set the file data for multipart/form-data
    files = {
        'file': open(image_path, 'rb'),
    }

    try:
        # Send a POST request to the endpoint with the image file
        response = requests.post(endpoint_url, headers=headers, files=files, verify=False)
        response.raise_for_status()  # Raise an exception for any HTTP error

        # Return the JSON response
        return response.json()

    except requests.exceptions.RequestException as e:
        print("Error occurred while making the request:", e)

def display_detected_objects(response):
    try:
        # Check if 'detectedObj' key is present
        if 'detectedObj' in response:
            detected_objects = response['detectedObj']
            print("Detected Objects:")
            for obj in detected_objects:
                print(obj)
            print("")

            # Turn off all LEDs
            GPIO.output(led_pin1, GPIO.LOW)
            GPIO.output(led_pin2, GPIO.LOW)

            # Check if 'Rotor Aircraft' is present
            if 'Rotor Aircraft' in detected_objects:
                # Turn on LED 1
                GPIO.output(led_pin1, GPIO.HIGH)

            # Check if 'Fixed Wing' is present
            if 'Fixed Wing' in detected_objects:
                # Turn on LED 2
                GPIO.output(led_pin2, GPIO.HIGH)

        else:
            print("'detectedObj' key not found in the JSON response.")

    except (json.JSONDecodeError, KeyError) as e:
        print("Error processing JSON response:", e)

def display_image(image_path, display_index, endpoint_url):
    try:
        pygame.init()

        # Get the display surface for the specific monitor
        display_info = pygame.display.Info()
        monitor_width = display_info.current_w
        monitor_height = display_info.current_h

        screen = pygame.display.set_mode((monitor_width, monitor_height), pygame.NOFRAME, display_index)
        image = pygame.image.load(image_path)
        image = pygame.transform.scale(image, (800, 480))  # Scale the image to the desired size
        screen.blit(image, (0, 0))
        pygame.display.flip()

        # Call the function to upload the image and get the JSON response
        json_response = upload_image(image_path, endpoint_url)

        # Call the function to display the detected objects and control the LEDs
        if json_response is not None:
            display_detected_objects(json_response)
        # Wait for 2 seconds
        time.sleep(2)

        pygame.quit()

        GPIO.output(led_pin1, GPIO.LOW)
        GPIO.output(led_pin2, GPIO.LOW)


    except pygame.error as e:
        print("Error displaying image:", e)

if __name__ == '__main__':
    # Check if image directory is provided as a command-line argument
    if len(sys.argv) < 2:
        print("Please provide the image directory path as a command-line argument.")
        sys.exit(1)

    # Get the image directory path from command-line arguments
    image_dir = sys.argv[1]

    # Specify the endpoint URL
    endpoint_url = 'https://custom-model-rt-flyingthings-standalone.apps.ocp4.davenet.local/detect'  # Replace with the actual endpoint URL

    # Turn off all LEDs initially
    GPIO.output(led_pin1, GPIO.LOW)
    GPIO.output(led_pin2, GPIO.LOW)

    # Loop through the images in the directory
    for filename in os.listdir(image_dir):
        if filename.endswith(".jpg"):
            image_path = os.path.join(image_dir, filename)

            print("Uploading file:", filename)

            display_image(image_path, 0, endpoint_url)            



            # Delay of 2 seconds before the next upload
            # time.sleep(2)
    # Cleanup the GPIO settings
    GPIO.cleanup()

