# RB-Tool
A simple tool for recording and replaying mouse clicks, extracting numbers from images, and recognizing handwritten numbers.

## Installation

1. Install the required libraries using the following commands:

```bash
pip install pyautogui
pip install pytesseract
pip install easyocr


## Usage

1. Run the `RB-Tool.py` script.
2. Switch between the two tabs to use the recording and OCR features.

## Recording

1. Click the "Start Recording" button.
2. Click the desired locations on the screen.
3. Click the "Stop Recording" button.
4. The recorded clicks will be displayed in the text box.
5. To replay the clicks, click the "Replay Clicks" button and enter the desired numbers in the input box.

## OCR

1. Click the "Scan" button to capture the entire screen or the "Handwritten" button to capture a specific region of the screen.
2. The captured image will be processed and the extracted text will be displayed in the text box.
3. To extract 18-digit numbers from the image, click the "Tote" button.

## Handwritten Number Recognition

1. Click the "Handwritten" button.
2. Capture the handwritten number using the "Scan" button.
3. The recognized number will be displayed in the text box.

## Support

Please open an issue on GitHub if you have any questions or problems.

## License

This project is licensed under the MIT License.
