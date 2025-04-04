# 🧠 Job Matching Service

A service that's deployed as a RESTful API that enables users to upload their CV and receive personalized job recommendations from a database. This project leverages LLMs for semantic understanding and Elasticsearch for fast, flexible search.

## 🚀 Features

- Upload a resume in PDF format and get back a ranked list of matching job listings
- LLM-based keyword extractions.
- Semantic search powered by Elasticsearch and custom embeddings via Hugging Face Transformers
- Results returned in a structured, user-friendly table format
- Allows filterings based on geographical locations in Vietnam, as well as the maximum and minimum salary.

## 🛠️ Tech Stack

- **FastAPI** – for building the RESTful API
- **Elasticsearch** – vector database for job listings and CV embeddings
- **Hugging Face Transformers** – for LLM-based extraction and embedding generation
- **Laravel** - PHP-based framework for interacting with the Python API.

## 📦 Installation
The project requires you to have a working Python installation on version 3.12.4, Laravel framework installed and a local deployment of Elasticsearch 8.x.
You can see the installation here: 
- [Laravel](https://laravel.com/docs/12.x/installation); 
- [Elasticsearch](https://docs.google.com/document/d/14OY33-r6B2cOvrUI7JpnKxih_iPCFfuv3lWSq9gIPJU/edit?usp=sharing)

1. **Clone the repository**
   ```bash
   git clone https://github.com/therook111/TopJobTesting.git
   cd job-matching-service
   ```
2. **Setup Python's virtual environment within the python_api library**
   ```bash
   python -m venv {venv name here}
   source venv/bin/activate # Or venv\Scripts\activate if you're on Windows!
   pip install -r requirements.txt
   ```
3. **Create a new Laravel project, and paste the assets of laravel_front into it, replacing every "duplicates"**
4. **Install Elasticsearch's PHP implementation**
   ```bash
   composer require elasticsearch/elasticsearch
   ```
5. **If done correctly, your project tree should look like this (sort of):**
   ```bash
   your_project_directory/
    ├── laravel_front/
    │   ├── app/
    │   ├── public/
    │   ├── resources/
    │   ├── routes/
    │   ├── .env.
    │   └── artisan
    ├── python_api/
    │   ├── Include
    │   ├── Lib
    │   ├── Scripts
    │   ├── other assets here
    │   └── sub.env
    ├── requirements.txt
    └── README.md
   ```
6. **Activate Python's FastAPI and Laravel**
   - Before running, please make sure to have a Google Gemini API key. Go to `python_api/sub.env` and fill in the missing variable, which is the API key and Elasticsearch's password.
   - Go to `python_api/backend/app.py` and press run
   - Run this in your project directory's terminal (bash or PowerShell)
     ```
     cd laravel_front
     php artisan serve
     ```
     
8. **Access http://127.0.0.1:8000 and see the result.**
   

