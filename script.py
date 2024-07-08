from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from pdf2image import convert_from_path
from preprocessing.languages import VietOCR, EngOCR, ConvertTables
from langdetect import detect
from preprocessing.file_handling import process_cv, process_grades

import shutil
import zipfile
import os
import cv2
import numpy as np

app = FastAPI()

@app.post("/upload")
async def upload_file(CV: UploadFile = File(...), grades: UploadFile = File(...), certificates: list[UploadFile] = File(...)):
    
    # CV pdf to image conversion
    cv_path = process_cv('krill_yourself.pdf', CV)
    # Grades image conversion
    
    grades_path = process_grades(grades=grades)

    # Certificates
    cert_paths = []
    for image in certificates:
        img_path = f"converted_{image.filename}"
        with open(img_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        cert_paths.append(img_path)

    
    zip_filename = "converted_files.zip"
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        zipf.write(cv_path)
        zipf.write(grades_path)
        for cert_image_path in cert_paths:
            zipf.write(cert_image_path)
    
    # Cleaning up temporary files
    os.remove(cv_path)
    os.remove(grades_path)
    for cert_image_path in cert_paths:
        os.remove(cert_image_path)
    
    # returning the zip file
    return FileResponse(zip_filename, media_type='application/zip', filename=zip_filename)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)