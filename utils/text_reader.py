import cv2
import pytesseract
import numpy as np
import re
from langdetect import detect
from pdf2image import convert_from_path
from pdfminer.high_level import extract_text
import spacy 

nlp = spacy.load('en_core_web_md')


pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'

def clean_text(text):
    doc = nlp(text)

    patterns = {'phone': r'(?:(?:\+84|0)\s*[3-9][0-9](?:[-.\s]?\d){7,8})',
                'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'}
    for PII in patterns:
        pattern = patterns[PII]
        text = re.sub(pattern, '', text)

    for ent in doc.ents:
        if ent.label_ in ['PERSON', 'FAC', 'GPE']:
            text = text.replace(ent.text, f'[{ent.label_}]')
    return text

class TextExtractor:
    def __init__(self, path):
        self.path = path
    def _check_readable(self):
        '''
        Check whether the PDF file is readable or it has to be OCR'd.
        '''
        try:
            text = extract_text(self.path)
            if text.strip():
                return 'readable'
        except:
            return 'non-readable'
    def extract_file(self):
        text = ''
        readable = self._check_readable()
        if readable == 'readable':
            text = extract_text(self.path)
            text = text.strip()
        else:
            images = convert_from_path(self.path, dpi=300)
            images = [cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR) for image in images]
            lang = detect(OCR(images[0]))
            if lang != 'vi':
                for image in images:
                    a = OCR(image)
                    text += a
            else:
                for image in images:
                    a = OCR(image)
                    text += a
        return text
            
class OCR:
    '''
    Wrapper class for using Tesseract-OCR for text images. Supported languages: English, Vietnamese
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
        text = pytesseract.image_to_string(img, config = self.config, lang=self.mode)
        if detect(text) == 'vie':
            text = pytesseract.image_to_string(img, config = self.config, lang='vie')
        return clean_text(text)
        
