import cv2
import pytesseract
import numpy as np
import re
import pandas as pd
import fitz
import os
pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'

def clean_text(text):
    patterns = [r'[\w+:]?\s?\d{3}\s?\d{3,4}\s?\d{4}', #Phone number
                r'[\w+:]?\s?[^\s]+@(gmail|hotmail|outlook|icloud).com', # Email Address
                r'[\w+:]?\s?(https?://)?www\.facebook\.com/.+' # Facebook link
                ]
    for pattern in patterns:
        text = re.sub(pattern, "", string=text)
    return text

class VietOCR:
    '''
    Wrapper class for using Tesseract-OCR for Vietnamese text data.
    '''
    def __init__(self, image, preprocessing=None, config = '--oem 3 --psm 3', desired_dpi=300):
        self.image = image
        self.preprocessing = preprocessing
        self.config = config
        self.desired_dpi = desired_dpi
    def _processing(self):
        
        self.actual_dpi = 72
        
        scaling_factor = self.desired_dpi / self.actual_dpi
        
        # Resize the image to achieve the desired DPI
        width = int(self.image.shape[1] * scaling_factor)
        height = int(self.image.shape[0] * scaling_factor)
        resized_image = cv2.resize(self.image, (width, height), interpolation=cv2.INTER_CUBIC)
        
        gray = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY)
        kernel = np.ones((5,5),np.uint8)
        
        if self.preprocessing == 'thresh':
            gray = cv2.threshold(gray, 0, 255,
		    cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        elif self.preprocessing == 'blur':
            gray = cv2.medianBlur(gray, 3)
        
        return gray
    
    def read_text(self):
        img = self._processing()
        text = pytesseract.image_to_string(img, config = self.config, lang='vie')
        return clean_text(text)
    
class EngOCR(VietOCR):
    '''
    Wrapper class for using Tesseract-OCR for English text data.
    '''
    def __init__(self, image, preprocessing=None, config = '--oem 3 --psm 3', desired_dpi = 300):
        self.image = image
        self.preprocessing = preprocessing
        self.config = config
        self.desired_dpi = desired_dpi
    def read_text(self):
        img = self._processing()
        text = pytesseract.image_to_string(img, config = self.config)
        return clean_text(text)
    
class ConvertTables:
    '''
    Wrapper class that uses PyMuPDF to read tables from a PDF file, and returns the data, in the form of a RTF file.
    '''
    def __init__(self, path):
        self.path = path 
    def _read_file(self):
        doc = fitz.open(self.path)
        
        return doc 
    def _conversion(self):
        doc = self._read_file()
        i = 1
        fin = []
        for page in doc:
            tabs = page.find_tables()
            if len(tabs.tables) == []:
                break
            if i == 1:
                tab = tabs[-1]
            else:
                tab = tabs[0]
                
            df = tab.to_pandas()
            
            x = df.shape[0]
            df = df.dropna(axis=1, thresh=0.5*x)
            y = df.shape[1]
            df = df.dropna(thresh = 0.5*y)
            
            df = df.reset_index()
            df = df.drop(['index'], axis=1)
            
            cols = df.iloc[0]
            df.columns = cols
            
            df = df.drop(0, axis=0)
            
            df = df.reset_index()
            df = df.drop(['index'], axis=1)
            fin.append(df)
        final = pd.concat(fin, axis=1)
        return final
    def read_result(self):
        self._conversion().to_csv('output.csv', index=False)
        with open('output.csv', encoding='utf-8') as f:
            txt = f.read()
        os.remove('output.csv')
        
        return txt