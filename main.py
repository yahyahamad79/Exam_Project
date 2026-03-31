 import streamlit as st
import fitz
from docx import Document
import re
import os
import tempfile

st.set_page_config(page_title="مولد أسئلة الامتحانات", page_icon="📝")

st.title("📝 نظام استخراج الأسئلة من PDF")
st.markdown("قم برفع ملف PDF لاستخراج الأسئلة وتصديرها كملف Word")

def extract_questions_from_pdf(text):
    questions = []
    sentences = re.split(r'[.\n]', text)
    count = 1
    
    for sentence in sentences:
        if len(sentence.strip()) > 40:
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
            if count > 20:
                break
    
    return questions

def create_word_document(questions):
    doc = Document()
    doc.add_heading('امتحان مادة الإدارة - الوحدة الثالثة (مستخرج حقيقي)', 0)
    
    for q in questions:
        p = doc.add_paragraph()
        p.add_run(f"[{q['level']}] ").bold = True
        p.add_run(f"{q['text']}")
        doc.add_paragraph("......................................................................")
    
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.docx')
    doc.save(temp_file.name)
    return temp_file.name

uploaded_file = st.file_uploader("اختر ملف PDF", type=["pdf"])

if uploaded_file is not None:
    st.success("✅ تم رفع الملف بنجاح")
    
    content = uploaded_file.read()
    doc = fitz.open(stream=content, filetype="pdf")
    
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    
    st.info(f"📄 عدد الصفحات: {len(doc)}")
    
    if st.button("🔍 استخراج الأسئلة"):
        with st.spinner("جاري المعالجة..."):
            questions = extract_questions_from_pdf(full_text)
            st.session_state.questions = questions
            st.success(f"✅ تم استخراج {len(questions)} سؤال")
    
    if 'questions' in st.session_state:
        st.subheader("📋 الأسئلة المستخرجة")
        for q in st.session_state.questions:
            with st.expander(f"سؤال {q['id']} - {q['level']}"):
                st.write(q['text'])
        
        if st.button("📥 تصدير كملف Word"):
            file_path = create_word_document(st.session_state.questions)
            
            with open(file_path, "rb") as f:
                st.download_button(
                    label="تحميل ملف Word",
                    data=f.read(),
                    file_name="Real_Exam.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
            
            os.remove(file_path)
else:
    st.warning("⚠️ يرجى رفع ملف PDF للبدء")

st.markdown("---")
st.markdown("© 2024 نظام استخراج الأسئلة | البروتوكول 2.0")
