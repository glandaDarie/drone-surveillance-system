import numpy as np
from djitellopy import Tello
import cv2, time, operator
import threading
from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QFont, QKeySequence
import sys, easygui

class Drone_Controller(threading.Thread):
	def __init__(self, frameName : str, detectorName : str, tello : Tello) -> None:
		threading.Thread.__init__(self)
		self.fileName = "threshold_checker_file.txt"
		self.delete_content_from_file()
		self.dPadMovement = 60 
		self.upDownMovement = 60 
		self.rotationAngleMovement = 360 
		self.init_GUI()
		self.readingFrames = True
		self.frameName = frameName
		self.tello = tello
		self.detectorName = detectorName
		self.set_default_setttings()
		self.upOrDown = True
		self.forwardOrBackwards = True
		self.currentTime = self.previousTime = time.time()
		self.outFileName = self.frameName + ".avi"
		self.window_controller.show()
		self.flagMoveForward = False
		self.flagMoveBackwards = False
		self.flagMoveLeft = False
		self.flagMoveRight = False
		self.flagMoveUp = False
		self.flagMoveDown = False
		self.flagRotate = False
		self.flagFlipForward = False
		self.pressedXToCloseGUI = False
		self.addBoxBlur = False
		self.error = 35 
	
	def delete_content_from_file(self) -> None:
		with open(self.fileName, "r+") as file:
			file.seek(0)
			file.truncate()
		file.close()
		
	def signal_forward(self) -> None: self.flagMoveForward = True; self.debug_write_to_file("Command : drone moves forward!\n")
	
	def signal_backward(self) -> None: self.flagMoveBackwards = True; self.debug_write_to_file("Command : drone moves backwards!\n")
	
	def signal_left(self) -> None: self.flagMoveLeft = True; self.debug_write_to_file("Command : drone moves left!\n")

	def signal_right(self) -> None: self.flagMoveRight = True; self.debug_write_to_file("Command : drone moves right!\n")

	def signal_up(self) -> None: self.flagMoveUp = True ; self.debug_write_to_file("Command : drone moves up!\n") 

	def signal_down(self) -> None: self.flagMoveDown = True; self.debug_write_to_file("Command : drone moves down!\n")  

	def signal_rotate(self) -> None: self.flagRotate = True; self.debug_write_to_file("Command : rotate drone!\n") 
	
	def signal_flip(self) -> None: self.flagFlipForward = True; self.debug_write_to_file("Command : flip drone!\n")

	def signal_toggle_box_blur(self) -> None: 
		if self.radionButton.isChecked(): self.addBoxBlur = True 
		else: self.addBoxBlur = False

	def value_in_bound_classical_movement(self, x) -> bool:
		if x >= 20 and x <= 500: return True 
		return False

	def value_in_bound_rotation(self, x) -> bool:
		if x >= 1 and x <= 3600 : return True
		return False

	def signal_modify_dpad_movement(self) -> None: 
		dPadMovementText = self.textBoxPad.text()
		if dPadMovementText.isdigit():
			dPadMovementText = int(dPadMovementText)
			if self.value_in_bound_classical_movement(dPadMovementText):
				self.dPadMovement = dPadMovementText
				self.textBoxPad.setText(f"cm's [D pad] = {str(self.dPadMovement)}") 
			else: self.textBoxPad.setText("cm's [D pad] = out of bound!")
		else: self.textBoxPad.setText("cm's [D pad] = not a number!")
	
	def signal_modify_up_down_movement(self) -> None:
		upDownMovementText = self.textBoxUpDown.text()
		if upDownMovementText.isdigit():
			upDownMovementText = int(upDownMovementText)
			if self.value_in_bound_classical_movement(upDownMovementText):
				self.upDownMovement = upDownMovementText
				self.textBoxUpDown.setText(f"cm's [up/down] = {str(self.upDownMovement)}") 
			else: self.textBoxUpDown.setText("cm's [up/down] = out of bound!")
		else: self.textBoxUpDown.setText("cm's [up/down] = not a number!")
	
	def signal_modify_rotation_movement(self) -> None:
		rotationMovement = self.textBoxRotation.text()
		if rotationMovement.isdigit():
			rotationMovement = int(rotationMovement)
			if self.value_in_bound_rotation(rotationMovement):
				self.rotationAngleMovement = rotationMovement
				self.textBoxRotation.setText(f"angle [rotation] = {str(self.rotationAngleMovement)}")
			else: self.textBoxRotation.setText("angle [rotation] = out of bound!")
		else: self.textBoxRotation.setText("angle [rotation] = not a number!")

	def init_GUI(self) -> None:
		self.init_main_window()
		self.init_right_button()
		self.init_left_button()
		self.init_forward_button()
		self.init_backward_button()
		self.init_middle_style_button_ignore()
		self.init_up_button()
		self.init_down_button()
		self.init_rotate_drone_button()
		self.init_flip_drone_button()
		self.init_dpad_textbox()
		self.init_dpad_button()
		self.init_up_down_text()
		self.init_up_down_button()
		self.init_rotation_text()
		self.init_rotation_button()
		self.init_box_blur_radio_button()

	def close_main_window_signal(self, event) -> None: self.pressedXToCloseGUI = True; event.accept()

	def init_main_window(self) -> None:
		windowSizeX, windowSizeY = 1000, 1400
		locationX, locationY = windowSizeX//4, windowSizeX//4
		self.window_controller = QMainWindow()
		self.window_controller.setGeometry(locationX, locationY, windowSizeX, windowSizeY)
		self.window_controller.setStyleSheet("QMainWindow" 
								"{"  
								"background-image : url(image_bacgkround_pyQT5_tello_drone.jpg);  background-repeat : no-repeat; background-position : center"
								"}"
								)
		self.window_controller.setWindowTitle("Joystick for Tello Drone")
		self.window_controller.setFixedSize(windowSizeX, windowSizeY)
		self.window_controller.closeEvent = self.close_main_window_signal
	
	def init_right_button(self) -> None:
		locationX, locationY = 550, 790
		windowSizeX, windowSizeY = 150, 150
		self.buttonRight = QtWidgets.QPushButton(self.window_controller)
		self.buttonRight.setGeometry(locationX, locationY, windowSizeX, windowSizeY)
		self.buttonRight.setText("Right")
		self.buttonRight.setStyleSheet("QPushButton"
                             "{"
                             "background-color : #8eb8c4; border : 5px solid black"
                             "}"
                             "QPushButton::hover"
                             "{"
                             "background-color : #96c48e;"
                             "}"
                             )
		self.buttonRight.setFont(QFont('Times', 8, QFont.Bold))
		self.buttonRight.clicked.connect(self.signal_right)
		shortcut = QtWidgets.QShortcut(QKeySequence(Qt.Key_Right), self.window_controller)
		shortcut.activated.connect(self.signal_right)

	def init_left_button(self) -> None:
		locationX, locationY = 250, 790
		windowSizeX, windowSizeY = 150, 150 
		self.buttonLeft = QtWidgets.QPushButton(self.window_controller)
		self.buttonLeft.setGeometry(locationX, locationY, windowSizeX, windowSizeY)
		self.buttonLeft.setText("Left")
		self.buttonLeft.setStyleSheet("QPushButton"
                             "{"
                             "background-color : #8eb8c4; border : 5px solid black"
                             "}"
                             "QPushButton::hover"
                             "{"
                             "background-color : #96c48e;"
                             "}"
                             )
		self.buttonLeft.setFont(QFont('Times', 8, QFont.Bold))
		self.buttonLeft.clicked.connect(self.signal_left)
		shortcut = QtWidgets.QShortcut(QKeySequence(Qt.Key_Left), self.window_controller)
		shortcut.activated.connect(self.signal_left)
	
	def init_forward_button(self) -> None:
		locationX, locationY = 400, 640
		windowSizeX, windowSizeY = 150, 150 
		self.buttonForward = QtWidgets.QPushButton(self.window_controller)
		self.buttonForward.setGeometry(locationX, locationY, windowSizeX, windowSizeY)
		self.buttonForward.setText("Forward")
		self.buttonForward.setStyleSheet("QPushButton"
                             "{"
                             "background-color : #8eb8c4; border : 5px solid black"
                             "}"
                             "QPushButton::hover"
                             "{"
                             "background-color : #96c48e;"
                             "}"
                             )
		self.buttonForward.setFont(QFont('Times', 8, QFont.Bold))
		self.buttonForward.clicked.connect(self.signal_forward)
		shortcut = QtWidgets.QShortcut(QKeySequence(Qt.Key_Up), self.window_controller)
		shortcut.activated.connect(self.signal_forward)
		
	def init_backward_button(self) -> None:
		locationX, locationY = 400, 940
		windowSizeX, windowSizeY = 150, 150 
		self.buttonBackward = QtWidgets.QPushButton(self.window_controller)
		self.buttonBackward.setGeometry(locationX, locationY, windowSizeX, windowSizeY)
		self.buttonBackward.setText("Backwards")
		self.buttonBackward.setStyleSheet("QPushButton"
                             "{"
                             "background-color : #8eb8c4; border : 5px solid black"
                             "}"
                             "QPushButton::hover"
                             "{"
                             "background-color : #96c48e;"
                             "}"
                             )
		self.buttonBackward.setFont(QFont('Times', 8, QFont.Bold))
		self.buttonBackward.clicked.connect(self.signal_backward)
		shortcut = QtWidgets.QShortcut(QKeySequence(Qt.Key_Down), self.window_controller)
		shortcut.activated.connect(self.signal_backward)
	
	def init_middle_style_button_ignore(self) -> None:
		locationX, locationY = 400, 790
		windowSizeX, windowSizeY = 150, 150 
		self.buttonMiddleIgnore = QtWidgets.QPushButton(self.window_controller)
		self.buttonMiddleIgnore.setGeometry(locationX, locationY, windowSizeX, windowSizeY)
		self.buttonMiddleIgnore.setText("")
		self.buttonMiddleIgnore.setStyleSheet("QPushButton"
                             "{"
                             "background-color : #ffffff; border : 5px solid black"
                             "}"
                             "QPushButton::hover"
                             "{"
                             "background-color : #96c48e;"
                             "}"
                             )
		self.buttonMiddleIgnore.setFont(QFont('Times', 8, QFont.Bold))
		self.buttonMiddleIgnore.setEnabled(False)
	
	def init_up_button(self) -> None:
		locationX, locationY = 180, 1200
		windowSizeX, windowSizeY = 150, 150 
		self.buttonUp = QtWidgets.QPushButton(self.window_controller)
		self.buttonUp.setGeometry(locationX, locationY, windowSizeX, windowSizeY)
		self.buttonUp.setText("Up")
		self.buttonUp.setStyleSheet("QPushButton"
                             "{"
                             "background-color : #8eb8c4; border-radius : 30; border : 5px solid black"
                             "}"
                             "QPushButton::hover"
                             "{"
                             "background-color : #96c48e;"
                             "}"
                             )
		self.buttonUp.setFont(QFont('Times', 8, QFont.Bold))
		self.buttonUp.clicked.connect(self.signal_up)
		shortcut = QtWidgets.QShortcut(QKeySequence(Qt.Key_U), self.window_controller)
		shortcut.activated.connect(self.signal_up)

	def init_down_button(self) -> None:
		locationX, locationY = 330, 1200
		windowSizeX, windowSizeY = 150, 150 
		self.buttonDown = QtWidgets.QPushButton(self.window_controller)
		self.buttonDown.setGeometry(locationX, locationY, windowSizeX, windowSizeY)
		self.buttonDown.setText("Down")
		self.buttonDown.setStyleSheet("QPushButton"
                             "{"
                             "background-color : #8eb8c4; border-radius : 30; border : 5px solid black"
                             "}"
                             "QPushButton::hover"
                             "{"
                             "background-color : #96c48e;"
                             "}"
                             )
		self.buttonDown.setFont(QFont('Times', 8, QFont.Bold))
		self.buttonDown.clicked.connect(self.signal_down)
		shortcut = QtWidgets.QShortcut(QKeySequence(Qt.Key_D), self.window_controller)
		shortcut.activated.connect(self.signal_down)

	def init_rotate_drone_button(self) -> None:
		locationX, locationY = 480, 1200
		windowSizeX, windowSizeY = 150, 150 
		self.buttonRotate = QtWidgets.QPushButton(self.window_controller)
		self.buttonRotate.setGeometry(locationX, locationY, windowSizeX, windowSizeY)
		self.buttonRotate.setText("Rotate")
		self.buttonRotate.setStyleSheet("QPushButton"
                             "{"
                             "background-color : #8eb8c4; border-radius : 30; border : 5px solid black"
                             "}"
                             "QPushButton::hover"
                             "{"
                             "background-color : #96c48e;"
                             "}"
                             )
		self.buttonRotate.setFont(QFont('Times', 8, QFont.Bold))
		self.buttonRotate.clicked.connect(self.signal_rotate)
		shortcut = QtWidgets.QShortcut(QKeySequence(Qt.Key_R), self.window_controller)
		shortcut.activated.connect(self.signal_rotate)

	def init_flip_drone_button(self) -> None:
		locationX, locationY = 630, 1200
		windowSizeX, windowSizeY = 150, 150 
		self.buttonRotate = QtWidgets.QPushButton(self.window_controller)
		self.buttonRotate.setGeometry(locationX, locationY, windowSizeX, windowSizeY)
		self.buttonRotate.setText("Flip")
		self.buttonRotate.setStyleSheet("QPushButton"
                             "{"
                             "background-color : #8eb8c4; border-radius : 30; border : 5px solid black"
                             "}"
                             "QPushButton::hover"
                             "{"
                             "background-color : #96c48e;"
                             "}"
                             )
		self.buttonRotate.setFont(QFont('Times', 8, QFont.Bold))
		self.buttonRotate.clicked.connect(self.signal_flip)
		shortcut = QtWidgets.QShortcut(QKeySequence(Qt.Key_F), self.window_controller)
		shortcut.activated.connect(self.signal_flip)
		
	def init_dpad_textbox(self) -> None:
		locationX, locationY = 100, 60
		textBoxSizeX, textBoxSizeY = 500, 100 
		self.textBoxPad = QtWidgets.QLineEdit(self.window_controller)
		self.textBoxPad.setGeometry(locationX, locationY, textBoxSizeX, textBoxSizeY)
		self.textBoxPad.setFont(QFont('Times', 13, QFont.Bold))
		self.textBoxPad.setText(f"cm's [D pad] = {str(self.dPadMovement)}")
	
	def init_dpad_button(self) -> None:
		locationX, locationY = 650, 60 
		buttonSizeX, buttonSizeY = 300, 100 
		self.buttonDPad = QtWidgets.QPushButton(self.window_controller)
		self.buttonDPad.setGeometry(locationX, locationY, buttonSizeX, buttonSizeY)
		self.buttonDPad.setText("Change dpad")
		self.buttonDPad.setStyleSheet("QPushButton"
                             "{"
                             "background-color : #8eb8c4; border-radius : 30; border : 5px solid black"
                             "}"
							 "QPushButton::hover"
                             "{"
                             "background-color : #8ea5c4;"
                             "}"
                             )
		self.buttonDPad.setFont(QFont('Times', 8, QFont.Bold))
		self.buttonDPad.clicked.connect(self.signal_modify_dpad_movement)
	
	def init_up_down_text(self) -> None:
		locationX, locationY = 100, 200
		textBoxSizeX, textBoxSizeY = 500, 100 
		self.textBoxUpDown = QtWidgets.QLineEdit(self.window_controller)
		self.textBoxUpDown.setGeometry(locationX, locationY, textBoxSizeX, textBoxSizeY)
		self.textBoxUpDown.setFont(QFont('Times', 13, QFont.Bold))
		self.textBoxUpDown.setText(f"cm's [up/down] = {str(self.upDownMovement)}")
	
	def init_up_down_button(self) -> None:
		locationX, locationY = 650, 200 
		buttonSizeX, buttonSizeY = 300, 100 
		self.buttonUpDown = QtWidgets.QPushButton(self.window_controller)
		self.buttonUpDown.setGeometry(locationX, locationY, buttonSizeX, buttonSizeY)
		self.buttonUpDown.setText("Change up/down")
		self.buttonUpDown.setStyleSheet("QPushButton"
                             "{"
                             "background-color : #8eb8c4; border-radius : 30; border : 5px solid black"
                             "}"
							 "QPushButton::hover"
                             "{"
                             "background-color : #8ea5c4;"
                             "}"
                             )
		self.buttonUpDown.setFont(QFont('Times', 8, QFont.Bold))
		self.buttonUpDown.clicked.connect(self.signal_modify_up_down_movement)
	
	def init_rotation_text(self) -> None:
		locationX, locationY = 100, 340
		textBoxSizeX, textBoxSizeY = 500, 100 
		self.textBoxRotation = QtWidgets.QLineEdit(self.window_controller)
		self.textBoxRotation.setGeometry(locationX, locationY, textBoxSizeX, textBoxSizeY)
		self.textBoxRotation.setFont(QFont('Times', 13, QFont.Bold))
		self.textBoxRotation.setText(f"angle [rotation] = {str(self.rotationAngleMovement)}")
	
	def init_rotation_button(self) -> None:
		locationX, locationY = 650, 340
		buttonSizeX, buttonSizeY = 300, 100 
		self.buttonRotation = QtWidgets.QPushButton(self.window_controller)
		self.buttonRotation.setGeometry(locationX, locationY, buttonSizeX, buttonSizeY)
		self.buttonRotation.setText("Change rotation angle")
		self.buttonRotation.setStyleSheet("QPushButton"
                             "{"
                             "background-color : #8eb8c4; border-radius : 30; border : 5px solid black"
                             "}"
							 "QPushButton::hover"
                             "{"
                             "background-color : #8ea5c4;"
                             "}"
                             )
		self.buttonRotation.setFont(QFont('Times', 8, QFont.Bold))
		self.buttonRotation.clicked.connect(self.signal_modify_rotation_movement)
	
	def init_box_blur_radio_button(self) -> None:
		locationX, locationY = 100, 480
		radioButtonSizeX, radioButtonxSizeY = 400, 100
		self.radionButton = QtWidgets.QRadioButton(self.window_controller)
		self.radionButton.setGeometry(locationX, locationY, radioButtonSizeX, radioButtonxSizeY)
		self.radionButton.setText("Add box blur")
		self.radionButton.setStyleSheet("QPushButton"
                             "{"
                             "background-color : #8eb8c4; border-radius : 30; border : 5px solid black"
                             "}"
							 "QPushButton::hover"
                             "{"
                             "background-color : #8ea5c4;"
                             "}"
                             )
		self.radionButton.setFont(QFont('Times', 13, QFont.Bold))
		self.radionButton.clicked.connect(self.signal_toggle_box_blur)

	def set_default_setttings(self) -> None:
		self.tello.connect()
		self.debug_write_to_file(f"Notification : tello battery when starting flying = {self.tello.get_battery()}\n")
		self.tello.streamon()
		self.tello.takeoff()

	def red_diagonals_over_photo(self, frame : np.ndarray, height : int, width : int) -> np.ndarray:
		cv2.line(frame, (0, 0), (width, height), (0, 0, 255), 10)
		cv2.line(frame, (width, 0), (0, height), (0, 0, 255), 10)
		return frame

	def pixel_level_box_blur(self, frame : np.ndarray, imageRows : int, imageColumns : int, radius=3) -> np.ndarray:
		outFrame = frame.copy()
		kernelRows, kernelColumns = (2 * radius + 1), (2 * radius + 1)
		if kernelRows != kernelColumns:
			print("Error!")
			return frame
		kernelSize = (kernelRows * kernelColumns)
		for i in range(radius, (imageRows-radius)): 
			for j in range(radius, (imageColumns-radius)):
				sumPixels = (0, 0, 0)
				for pixel in [(i-1), (j+1), (i, j+1), (i+1, j+1), (i-1, j), (i, j), (i+1, j), (i-1, j-1), (i, j-1), (i+1), (j-1)]:
					sumPixels = tuple(map(operator.add, sumPixels, frame[i][j]))
				outFrame[i][j] = tuple(map(operator.floordiv, sumPixels, (kernelSize, kernelSize, kernelSize)))
		return outFrame

	def open_cv_bilaterial_filter(self, frame : np.ndarray, diameter : int, sigmaColor : int, sigmaSpace: int) -> np.ndarray:
		return cv2.bilateralFilter(frame, diameter, sigmaColor, sigmaSpace)

	def rgb_to_grayscale_conversion(self, frame : np.ndarray, flag : bool) -> np.ndarray:
		if flag:
			return (frame[:,:,0] + frame[:,:,1] + frame[:,:,2]) // 3
		return frame

	def grayscale_to_rgb_conversion(self, frame : np.ndarray) -> np.ndarray:
		return cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
	
	def create_feature_matcher_and_check_movement(self, currentFrame : np.ndarray, previousFrame : np.ndarray, \
		index : int, numberMatches : int) -> np.ndarray:
		if self.detectorName == "sift" or self.detectorName == "sift".upper(): detector = cv2.SIFT_create()
		elif self.detectorName == "orb" or self.detectorName == "orb".upper(): detector = cv2.ORB_create()
		_, descriptorsCurrent = detector.detectAndCompute(currentFrame, None)
		_, descriptorsPrevious = detector.detectAndCompute(previousFrame, None)
		bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=True) 
		matches = bf.match(descriptorsCurrent, descriptorsPrevious)
		if index % 10 == 0: numberMatches = len(matches)
		threshold = int(numberMatches * ((100 - self.error) / 100))
		if len(matches) > threshold: flag = True; ifMovement = "No Movement present!"
		else: flag = False; ifMovement = "Movement present!"
		self.debug_write_to_file(f"Threshold = {str(threshold)} < number matches = {str(len(matches))} | {ifMovement}\n")
		if flag: return (numberMatches, True)
		return (numberMatches, False)
	
	def debug_write_to_file(self, content : str) -> None:
		with open(self.fileName, "a+") as file:
			file.write(content)
		file.close()

	def run(self) -> None: 
		while self.readingFrames: 
			if self.flagMoveForward: self.tello.move_forward(self.dPadMovement); self.flagMoveForward = False
			elif self.flagMoveBackwards: self.tello.move_back(self.dPadMovement); self.flagMoveBackwards = False
			elif self.flagMoveLeft: self.tello.move_left(self.dPadMovement); self.flagMoveLeft = False
			elif self.flagMoveRight: self.tello.move_right(self.dPadMovement); self.flagMoveRight = False
			elif self.flagMoveUp: self.tello.move_up(self.upDownMovement); self.flagMoveUp = False
			elif self.flagMoveDown: self.tello.move_down(self.upDownMovement); self.flagMoveDown = False
			elif self.flagRotate: self.error = 95; self.tello.rotate_counter_clockwise(self.rotationAngleMovement); self.flagRotate = False; self.error = 35 
			elif self.flagFlipForward: self.tello.flip_back(); self.flagFlipForward = False
			else: self.tello.send_rc_control(0, 0, 0, 0) #send this again so the frame rate does not drop 
		self.debug_write_to_file(f"Notification : tello battery when landing = {self.tello.get_battery()}\n")
		self.tello.land()
		self.tello.streamoff()
		self.window_controller.close() #close pyQT5 window

	def read_frames(self) -> None:
		currentFrame = self.tello.get_frame_read().frame
		currentFrame = self.rgb_to_grayscale_conversion(currentFrame, True)
		height, width, _ = self.tello.get_frame_read().frame.shape
		writer = cv2.VideoWriter(self.outFileName, cv2.VideoWriter_fourcc(*'XVID'), 30, (width, height))
		currentTime = time.time()
		index, numberMatches = 0, 0 
		startTimeDrawDiagonals, endTimeDrawDiagonals = None, time.time()
		while self.readingFrames:
			previousTime = currentTime
			previousFrame = currentFrame.copy()
			currentFrame = self.tello.get_frame_read().frame
			currentFrame = self.rgb_to_grayscale_conversion(currentFrame, True)
			numberMatches, doesNotExistMovement = self.create_feature_matcher_and_check_movement(currentFrame, previousFrame, index, numberMatches) 
			currentTime = time.time()
			actualFrame = self.tello.get_frame_read().frame
			fps = int(1 / (currentTime - previousTime)) 
			cv2.putText(img=actualFrame, text=f"FPS = {str(fps)}", org=(40, 40), \
                    fontFace=cv2.FONT_HERSHEY_COMPLEX, fontScale=1.0, color=(0, 255, 0), thickness=6)
			if doesNotExistMovement is False: startTimeDrawDiagonals = endTimeDrawDiagonals
			endTimeDrawDiagonals = time.time()
			self.debug_write_to_file(f"Start time draw diagonals = {str(startTimeDrawDiagonals)}, end time draw diagonals = {str(endTimeDrawDiagonals)}\n")
			if doesNotExistMovement is True and startTimeDrawDiagonals is None:  
				actualFrame = self.red_diagonals_over_photo(actualFrame, height, width)
				actualFrame = self.open_cv_bilaterial_filter(actualFrame, 15, 75, 75)
				if self.addBoxBlur: 
					actualFrame = self.pixel_level_box_blur(actualFrame, height, width, 7) # does not work well with SIFT in this instance here  
			elif startTimeDrawDiagonals is not None: 
				actualFrame = self.open_cv_bilaterial_filter(actualFrame, 15, 75, 75)
				writer.write(actualFrame) 
				if int(endTimeDrawDiagonals - startTimeDrawDiagonals) > 2: 
					startTimeDrawDiagonals = None
			cv2.imshow(self.frameName, actualFrame)
			if (cv2.waitKey(1) & 0xFF == ord('q')) or self.pressedXToCloseGUI:
				self.readingFrames = False 
			index += 1
		writer.release()
		
if __name__ == "__main__":
	detectorNames = ["sift", "orb"]
	detectorName = "sift"
	if detectorName not in detectorNames:
		easygui.msgbox("This detector does not exist!", title="Error")
		sys.exit(1)
	application_gui = QApplication(sys.argv)
	droneController = Drone_Controller("Drone_video_surverillance", detectorName, tello = Tello())
	droneController.start()
	droneController.read_frames()
	sys.exit(application_gui.exec_())