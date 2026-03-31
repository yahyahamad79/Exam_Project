# main.py
import streamlit as st
import fitz  # PyMuPDF للمعالجة الحقيقية
from docx import Document
import re
import io
import tempfile
import os

# إعداد صفحة Streamlit
st.set_page_config(
    page_title="مولد الامتحانات الذكي",
    page_icon="📝",
    layout="wide"
)

# إضافة CSS للتنسيق العربي
st.markdown("""
    <style>
        .stApp {
            direction: rtl;
            text-align: right;
        }
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin-bottom: 30px;
        }
        .question-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin: 10px 0;
            border-right: 4px solid #667eea;
        }
        .level-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            margin-left: 10px;
        }
        .level-basic {
            background: #28a745;
            color: white;
        }
        .level-medium {
            background: #ffc107;
            color: black;
        }
        .level-advanced {
            background: #dc3545;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

# دالة استخراج الأسئلة الحقيقية من النص
def extract_questions_from_pdf(text):
    questions = []
    # البحث عن الفقرات التي تحتوي على مفاهيم أساسية
    sentences = re.split(r'[.\n]', text)
    count = 1
    
    for sentence in sentences:
        if len(sentence.strip()) > 40:  # نختار الجمل الغنية بالمعلومات
            # تحديد مستوى الصعوبة بناءً على الكلمات المفتاحية
            level = "بسيط"
            if "بسبب" in sentence or "بينما" in sentence or "الفجوة" in sentence:
                level = "متوسط"
            if "التحوط" in sentence or "الاستراتيجي" in sentence or "تحليل" in sentence:
                level = "متقدم"
            
            # تنظيف النص
            clean_text = sentence.strip()
            if clean_text and not clean_text.endswith('؟'):
                clean_text += "؟"
            
            questions.append({
                "id": count,
                "level": level,
                "text": clean_text,
                "page": f"صفحة {count}"
            })
            count += 1
            if count > 30:  # نكتفي بـ 30 سؤالاً
                break
    return questions

# دالة استخراج النص من PDF
def extract_text_from_pdf(uploaded_file):
    try:
        # قراءة محتوى الملف
        pdf_bytes = uploaded_file.read()
        # فتح ملف PDF
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        full_text = ""
        for page_num, page in enumerate(doc, 1):
            page_text = page.get_text()
            full_text += f"\n--- صفحة {page_num} ---\n{page_text}"
        
        return full_text
    except Exception as e:
        st.error(f"حدث خطأ في معالجة ملف PDF: {str(e)}")
        return None

# دالة تصدير الأسئلة إلى Word
def export_to_word(questions):
    try:
        doc = Document()
        
        # إضافة العنوان
        title = doc.add_heading('امتحان مادة الإدارة - الوحدة الثالثة', 0)
        title.alignment = 1  # توسيط
        
        # إضافة معلومات الامتحان
        doc.add_paragraph(f'عدد الأسئلة: {len(questions)}')
        doc.add_paragraph('الدرجة الكلية: 100 درجة')
        doc.add_paragraph('الزمن: ساعتان')
        doc.add_paragraph('ملاحظة: أجب عن جميع الأسئلة')
        doc.add_paragraph('')
        
        # إضافة الأسئلة
        for i, q in enumerate(questions, 1):
            # إضافة السؤال
            p = doc.add_paragraph()
            
            # إضافة مستوى الصعوبة
            level_run = p.add_run(f"[{q['level']}] ")
            level_run.bold = True
            
            # إضافة نص السؤال
            question_run = p.add_run(f"{i}. {q['text']}")
            question_run.bold = True
            
            # إضافة مساحة للإجابة
            doc.add_paragraph("الإجابة: ......................................................................")
            doc.add_paragraph("")
        
        # حفظ المستند في الذاكرة
        file_stream = io.BytesIO()
        doc.save(file_stream)
        file_stream.seek(0)
        
        return file_stream
    except Exception as e:
        st.error(f"حدث خطأ في إنشاء ملف Word: {str(e)}")
        return None

# دالة تصدير الأسئلة إلى نص
def export_to_text(questions):
    text_content = "=" * 50 + "\n"
    text_content += "امتحان مادة الإدارة - الوحدة الثالثة\n"
    text_content += "=" * 50 + "\n\n"
    
    for i, q in enumerate(questions, 1):
        text_content += f"[{q['level']}] السؤال {i}: {q['text']}\n"
        text_content += "الإجابة: ________________________________________________\n\n"
    
    return text_content

# الواجهة الرئيسية
def main():
    # العنوان الرئيسي
    st.markdown("""
        <div class="main-header">
            <h1>📝 مولد الامتحانات الذكي</h1>
            <p>قم برفع ملف PDF لاستخراج أسئلة ذكية بناءً على المحتوى الحقيقي</p>
        </div>
    """, unsafe_allow_html=True)
    
    # عمودين للتنسيق
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### 📤 رفع الملف")
        uploaded_file = st.file_uploader(
            "اختر ملف PDF",
            type=['pdf'],
            help="قم برفع ملف PDF لاستخراج الأسئلة منه"
        )
        
        if uploaded_file:
            st.success(f"✅ تم رفع الملف: {uploaded_file.name}")
            
            # زر لبدء المعالجة
            if st.button("🚀 استخراج الأسئلة", type="primary", use_container_width=True):
                with st.spinner("جاري معالجة الملف واستخراج الأسئلة..."):
                    # استخراج النص من PDF
                    full_text = extract_text_from_pdf(uploaded_file)
                    
                    if full_text:
                        # استخراج الأسئلة
                        questions = extract_questions_from_pdf(full_text)
                        
                        if questions:
                            # حفظ الأسئلة في session state
                            st.session_state.questions = questions
                            st.session_state.full_text = full_text
                            st.success(f"✅ تم استخراج {len(questions)} سؤالاً بنجاح!")
                            st.balloons()
                        else:
                            st.warning("⚠️ لم يتم العثور على أسئلة في الملف. حاول رفع ملف آخر.")
    
    with col2:
        st.markdown("### 📋 الأسئلة المستخرجة")
        
        # عرض الأسئلة إذا كانت موجودة في session state
        if 'questions' in st.session_state and st.session_state.questions:
            questions = st.session_state.questions
            
            # إحصائيات سريعة
            levels = {}
            for q in questions:
                level = q['level']
                levels[level] = levels.get(level, 0) + 1
            
            col_stats1, col_stats2, col_stats3 = st.columns(3)
            with col_stats1:
                st.metric("إجمالي الأسئلة", len(questions))
            with col_stats2:
                st.metric("أسئلة بسيطة", levels.get('بسيط', 0))
            with col_stats3:
                st.metric("أسئلة متوسطة/متقدمة", levels.get('متوسط', 0) + levels.get('متقدم', 0))
            
            # عرض الأسئلة في tab
            tab1, tab2 = st.tabs(["📝 عرض الأسئلة", "🔧 خيارات التصدير"])
            
            with tab1:
                # فلتر حسب المستوى
                filter_level = st.selectbox(
                    "فلتر حسب المستوى:",
                    ["الكل", "بسيط", "متوسط", "متقدم"]
                )
                
                # عرض الأسئلة
                for q in questions:
                    if filter_level == "الكل" or q['level'] == filter_level:
                        # تحديد لون البادج
                        level_class = "level-basic" if q['level'] == "بسيط" else "level-medium" if q['level'] == "متوسط" else "level-advanced"
                        
                        st.markdown(f"""
                            <div class="question-card">
                                <div>
                                    <span class="level-badge {level_class}">{q['level']}</span>
                                    <strong>السؤال {q['id']}:</strong>
                                </div>
                                <p style="margin-top: 10px;">{q['text']}</p>
                            </div>
                        """, unsafe_allow_html=True)
            
            with tab2:
                st.markdown("#### 📥 خيارات التصدير")
                
                col_export1, col_export2 = st.columns(2)
                
                with col_export1:
                    # تصدير إلى Word
                    if st.button("📄 تصدير إلى Word", use_container_width=True):
                        with st.spinner("جاري إنشاء ملف Word..."):
                            word_file = export_to_word(questions)
                            if word_file:
                                st.download_button(
                                    label="📥 تحميل ملف Word",
                                    data=word_file,
                                    file_name="الامتحان_المستخرج.docx",
                                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                    use_container_width=True
                                )
                
                with col_export2:
                    # تصدير إلى نص
                    if st.button("📝 تصدير إلى نص", use_container_width=True):
                        text_content = export_to_text(questions)
                        st.download_button(
                            label="📥 تحميل ملف نصي",
                            data=text_content,
                            file_name="الامتحان_المستخرج.txt",
                                    mime="text/plain",
                            use_container_width=True
                        )
                
                # عرض معاينة النص الأصلي
                with st.expander("📄 معاينة النص المستخرج من PDF"):
                    if 'full_text' in st.session_state:
                        st.text_area("النص الأصلي:", st.session_state.full_text, height=200, disabled=True)
        else:
            st.info("💡 قم برفع ملف PDF واضغط على زر 'استخراج الأسئلة' لعرض الأسئلة هنا")
    
    # شريط جانبي مع معلومات إضافية
    with st.sidebar:
        st.markdown("### ℹ️ معلومات عن التطبيق")
        st.markdown("""
        **كيف يعمل التطبيق؟**
        
        1. قم برفع ملف PDF (كتاب، محاضرة، أو أي نص تعليمي)
        2. يقوم التطبيق باستخراج النص وتحليله
        3. يتم تحويل الجمل الغنية بالمعلومات إلى أسئلة
        4. يتم تصنيف الأسئلة حسب مستوى الصعوبة
        
        **مستويات الصعوبة:**
        - 🟢 **بسيط**: أسئلة أساسية ومباشرة
        - 🟡 **متوسط**: أسئلة تحتاج إلى فهم وتحليل
        - 🔴 **متقدم**: أسئلة معقدة تتطلب تفكير عميق
        
        **ملاحظات:**
        - يعمل التطبيق مع ملفات PDF النصية (غير الممسوحة ضوئياً)
        - كلما كان النص غنياً بالمعلومات، كانت الأسئلة أفضل
        - يمكن تصدير الأسئلة إلى Word أو ملف نصي
        """)
        
        st.markdown("---")
        st.markdown("### 🛠️ تقنيات مستخدمة")
        st.markdown("""
        - **Streamlit**: واجهة المستخدم
        - **PyMuPDF**: معالجة PDF
        - **python-docx**: تصدير Word
        - **تعبير منتظم**: تحليل النص
        """)

if __name__ == "__main__":
    main()
