from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from langdetect import detect
from pdf2image import convert_from_path

import shutil
import zipfile
import os
import cv2
import numpy as np

from preprocessing.languages import EngOCR, VietOCR, ConvertTables

def text_to_rtf_cv(content):
    content = content.replace('\n', '\\par ')
    rtf_content = f"""{{\\rtf1\\ansi\\deff0
{{\\fonttbl{{\\f0\\fswiss\\fcharset0 Arial;}}}}
{{\\colortbl ;\\red0\\green0\\blue255;}}
\\f0\\fs28\\b {{\\cf1 {"Curriculum Vitae"}}}\\par
\\fs24\\b0 {content}
}}"""
    return rtf_content

def process_cv(destination='temp.pdf', CV: UploadFile = File(...)):
    '''
    Utility function for processing a CV, assuming PDF file.
    '''
    if CV.content_type != "application/pdf":
        raise Exception("PDF file only.")
    else:
        with open(destination, "wb") as buffer:
            shutil.copyfileobj(CV.file, buffer)

        images = convert_from_path(destination, first_page=0, last_page=1)
        image = cv2.cvtColor(np.array(images[0]), cv2.COLOR_RGB2BGR)
        
        content = EngOCR(image).read_text()
        if detect(content) == 'vi':
            content = VietOCR(image).read_text
            
        content = text_to_rtf_cv(content)
        
        cv_path = f"converted_cv.rtf"
        
        with open(cv_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        os.remove(destination)
        return cv_path

def process_grades(destination='temp.pdf', grades: UploadFile = File(...)):
    if grades.content_type not in ["application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "application/pdf"]:
        raise Exception("PDF file only.")
    elif grades.content_type == "application/pdf":
        
        with open(destination, "wb") as buffer:
            shutil.copyfileobj(grades.file, buffer)
        
        obj = ConvertTables(destination)
        output = obj.read_result()

        path = 'converted_grades.txt'
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(output)
            
        os.remove(destination)
        return path
        
    else:
        pass
    