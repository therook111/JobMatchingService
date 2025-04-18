<!-- resources/views/job-matching/index.blade.php -->
@extends('layouts.app')

@section('content')
<div class="upload-form">
    <h2>Create your user profile!</h2>
    <form id="uploadForm" action="{{ route('upload.cv') }}" method="post" enctype="multipart/form-data">
        @csrf
        <div class="upload-section">
            <h3>Upload CV</h3>
            <div class="upload-box" id="cvUploadBox">
                <div class="upload-info">
                    <div class="upload-icon">⬆️</div>
                    <div class="upload-text">
                        <strong>Drag and drop file here</strong>
                        <span>Limit 20MB per file • PDF</span>
                    </div>
                </div>
                <button type="button" class="browse-button" onclick="document.getElementById('cvInput').click()">Browse files</button>
            </div>
            <input type="file" id="cvInput" name="cv" accept=".pdf" style="display: none;" onchange="handleFileSelect(this, 'cvUploadBox', 'cvFileInfo')">
            <div id="cvFileInfo" class="file-info hidden"></div>
        </div>

        <button type="submit" class="submit-button" disabled>Submit Files</button>
        <p style="color: gray; font-size: 14px; margin-top: 5px; text-align: center;">
            While we accept scanned PDFs as your CV, we strongly recommend that you upload your CV in a text-based form for the optimal matching result!
        </p>
    </form>
</div>
@endsection

@section('styles')
<style>
    body {
        font-family: 'Nunito', sans-serif;
        max-width: 800px;
        margin: 50px auto;
        padding: 20px;
    }
    h1 {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    h1::before {
        content: "🔗";
        font-size: 24px;
    }
    .upload-form {
        max-width: 800px;
        margin: auto;
        padding: 20px;
        border: 1px solid #ccc;
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
    }
    .upload-form h2 {
        margin-bottom: 20px;
        text-align: center;
    }
    .upload-section {
        margin-bottom: 20px;
    }
    .upload-box {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background-color: #f8f8ff;
        border-radius: 8px;
        padding: 15px 20px;
        margin: 20px auto;
    }
    .upload-info {
        display: flex;
        align-items: center;
        gap: 15px;
    }
    .upload-icon {
        color: #a0a0a0;
        font-size: 24px;
    }
    .upload-text {
        display: flex;
        flex-direction: column;
    }
    .upload-text strong {
        color: #606060;
        font-size: 16px;
        font-weight: normal;
    }
    .upload-text span {
        color: #a0a0a0;
        font-size: 14px;
    }
    .browse-button {
        background-color: #ffffff;
        border: 1px solid #d1d5db;
        color: #374151;
        padding: 8px 12px;
        border-radius: 6px;
        font-size: 14px;
        cursor: pointer;
        transition: background-color 0.3s;
    }
    .browse-button:hover {
        background-color: #f9fafb;
    }
    .file-info {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-top: 10px;
        background-color: #f0f0f0;
        padding: 5px;
        border-radius: 5px;
    }
    .file-icon {
        font-size: 20px;
    }
    .success-message {
        color: green;
        margin-top: 20px;
    }
    .hidden {
        display: none;
    }
    .submit-button {
        background-color: #4CAF50;
        color: white;
        padding: 12px 20px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 16px;
        transition: background-color 0.3s ease;
        display: block;
        margin: 20px auto;
        width: 200px;
    }
    .submit-button:hover {
        background-color: #45a049;
    }
    .submit-button:focus {
        outline: none;
        box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.5);
    }
    .submit-button:active {
        transform: translateY(1px);
    }
    .submit-button:disabled {
        background-color: #d1d5db; 
        color: #9ca3af; 
        cursor: not-allowed; 
        border: 1px solid #d1d5db; 
    }
</style>
@endsection

@section('scripts')
<script>
    document.getElementById('uploadForm').addEventListener('submit', function(event) {
        const CV = document.getElementById('cvInput').files[0];
        if (!CV) {
            alert('Please select a CV file.');
            event.preventDefault();
            return;
        }
        if (CV.type !== 'application/pdf') {
            alert('CV must be a PDF file.');
            event.preventDefault();
            return;
        }
    });

    document.addEventListener('DOMContentLoaded', function () {
        const cvInput = document.getElementById('cvInput');
        const submitButton = document.querySelector('.submit-button');

        submitButton.disabled = true;

        cvInput.addEventListener('change', function () {
            const file = cvInput.files[0];

            if (file) {
                if (file.size <= 20 * 1024 * 1024) {
                    submitButton.disabled = false;
                } else {
                    alert('The file exceeds the 20MB limit.');
                    cvInput.value = '';
                    submitButton.disabled = true;
                }
            } else {
                submitButton.disabled = true; 
            }
        });
    });

                
    function handleFileSelect(input, uploadBoxId, fileInfoId) {
        const file = input.files[0];
        if (file) {
            document.getElementById(uploadBoxId).querySelector('.browse-button').style.display = 'none';
            displayFileInfo(file, fileInfoId);
        }
    }

    function handleMultipleFileSelect(input, uploadBoxId, fileInfoId) {
        const files = input.files;
        const fileInfoDiv = document.getElementById(fileInfoId);
        fileInfoDiv.innerHTML = '';
        
        for (let i = 0; i < files.length && i < 10; i++) {
            displayFileInfo(files[i], fileInfoId);
        }

        if (files.length >= 10) {
            document.getElementById(uploadBoxId).querySelector('.browse-button').style.display = 'none';
        }
    }

    function displayFileInfo(file, fileInfoId) {
        const fileInfoDiv = document.getElementById(fileInfoId);
        const fileInfo = document.createElement('div');
        fileInfo.className = 'file-info';
        fileInfo.innerHTML = `
            <span class="file-icon">📄</span>
            <span>${file.name}</span>
            <span>${(file.size / 1024).toFixed(1)} KB</span>
            <span style="margin-left: auto; cursor: pointer;" onclick="removeFile(this, '${fileInfoId}')">❌</span>
        `;
        fileInfoDiv.appendChild(fileInfo);
        fileInfoDiv.classList.remove('hidden');
    }

    function removeFile(element, fileInfoId) {
        const fileInfo = element.closest('.file-info');
        fileInfo.remove();
        
        const fileInfoDiv = document.getElementById(fileInfoId);
        if (fileInfoDiv.children.length === 0) {
            const uploadBoxId = fileInfoId.replace('FileInfo', 'UploadBox');
            document.getElementById(uploadBoxId).querySelector('.browse-button').style.display = 'block';
            fileInfoDiv.classList.add('hidden');
        }

        // Reset the file input
        const inputId = fileInfoId.replace('FileInfo', 'Input');
        document.getElementById(inputId).value = '';
        
        // Disable submit button
        document.querySelector('.submit-button').disabled = true;
    }
</script>
@endsection