import pyautogui
import time

print("Move your mouse to the desired location...")
time.sleep(3) # Give yourself 3 seconds to move the mouse

x, y = pyautogui.position()
print(f"The mouse is currently at X: {x}, Y: {y}")