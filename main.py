 from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import fitz  # PyMuPDF للمعالجة الحقيقية
from docx import Document
from pydantic import BaseModel
from typing import List
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Question(BaseModel):
    id: int
    text: str
    level: str
    page: str

# دالة استخراج الأسئلة الحقيقية من النص (البروتوكول 2.0)
def extract_questions_from_pdf(text):
    questions = []
    # البحث عن الفقرات التي تحتوي على مفاهيم أساسية (يُعرف، يتكون، يهدف)
    # هذه خوارزمية مبسطة لتحويل النص إلى أسئلة حقيقية
    sentences = re.split(r'[.\n]', text)
    count = 1
    
    for sentence in sentences:
        if len(sentence.strip()) > 40: # نختار الجمل الغنية بالمعلومات
            level = "بسيط"
            if "بسبب" in sentence or "بينما" in sentence or "الفجوة" in sentence:
                level = "متوسط"
            if "التحوط" in sentence or "الاستراتيجي" in sentence:
                level = "متقدم"
            
            questions.append({
                "id": count,
                "level": level,
                "text": sentence.strip() + "؟",
                "page": "مستخرج من النص"
            })
            count += 1
            if count > 20: break # نكتفي بـ 20 سؤالاً كعينة أولى
    return questions

@app.post("/process")
async def process_pdf(file: UploadFile = File(...)):
    content = await file.read()
    # فتح ملف الـ PDF الحقيقي المرفوع
    doc = fitz.open(stream=content, filetype="pdf")
    
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    
    # استخراج الأسئلة من النص الحقيقي المرفوع
    real_questions = extract_questions_from_pdf(full_text)
    
    return {"questions": real_questions}

@app.post("/export-word")
async def export_word(questions: List[Question]):
    doc = Document()
    doc.add_heading('امتحان مادة الإدارة - الوحدة الثالثة (مستخرج حقيقي)', 0)
    
    for q in questions:
        p = doc.add_paragraph()
        p.add_run(f"[{q.level}] ").bold = True
        p.add_run(f"{q.text}")
        doc.add_paragraph("......................................................................")

    file_path = "final_exam.docx"
    doc.save(file_path)
    return FileResponse(file_path, filename="Real_Exam.docx")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
