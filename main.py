 from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import fitz  # PyMuPDF
import os
from docx import Document
from pydantic import BaseModel
from typing import List
import re

app = FastAPI()

# تأكد أن كل الأسطر التالية تبدأ من أقصى اليسار أو تتبع إزاحة منطقية
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# بقية الكود...
