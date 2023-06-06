# Surveillance Camera System using Feature Detectors for Tello Drone

This repository contains the code and documentation for a surveillance camera system implemented using feature detectors for the Tello Drone. The system utilizes computer vision techniques to detect and track movement in real-time, making it suitable for security and monitoring applications.

## Key Features

- Real-time frame analysis: The system captures frames from the Tello Drone's camera and performs feature detection and matching to detect movement.
- Feature detection and matching: The system utilizes feature detection algorithms, such as SIFT or ORB, to extract key points and descriptors from the frames. These features are then matched using a brute force matcher algorithm with L2 loss.
- Movement detection and tracking: The system compares the features of consecutive frames and calculates the number of matches. By setting a threshold based on the number of matches and a predefined error percentage, the system determines if there is movement or no movement present.
- Video output: When movement is detected, the system saves video files with highlighted regions of movement for further analysis and review.
- Optional image processing algorithms: The system provides optional features such as pixel-level box blur and bilateral filtering to enhance the captured frames and improve the accuracy of movement detection.
- User-friendly GUI: The system includes a graphical user interface that allows users to control the drone's movement and adjust parameters such as speed and angle.

## Dependencies

- OpenCV: Used for capturing frames, image processing, and feature detection.
- NumPy: Required for array manipulation and computations.
- TelloPy: Python library for interacting with the Tello Drone.
- QT5: GUI framework for the graphical user interface.

## Installation

1. Clone the repository: `git clone https://github.com/glandaDarie/drone-surveillance-system.git`
2. Install the required dependencies: `pip install -r requirements.txt`
3. Set up the Tello Drone and establish a connection following the instructions provided by the manufacturer.

## Usage

1. Run the provided Python script to start the surveillance camera system: `python drone_surveillance_system.py`
2. Use the GUI to control the drone's movement and adjust parameters.
3. The system will capture frames, detect movement, and save video files as needed.
4. Review the generated videos and analyze the detected movement.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your improvements.

## License

This project is licensed under the [MIT License](LICENSE).
