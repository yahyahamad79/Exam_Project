 # main.py
import streamlit as st
import fitz  # PyMuPDF للمعالجة الحقيقية
from docx import Document
import re
import io
from collections import Counter

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
            transition: transform 0.2s;
        }
        .question-card:hover {
            transform: translateX(-5px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
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
        .stats-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 15px;
            border-radius: 10px;
            color: white;
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

# دالة محسنة لاستخراج الأسئلة من النص
def extract_questions_from_pdf(text):
    questions = []
    
    # تنظيف النص
    text = text.replace('\n', ' ')
    text = re.sub(r'\s+', ' ', text)
    
    # قائمة الكلمات المفتاحية للعثور على جمل مهمة
    keywords = [
        'يعرف', 'يُعرف', 'يعتبر', 'هو', 'تعتبر', 'تتمثل', 'يتمثل',
        'يتكون', 'يتضمن', 'يشمل', 'يتكون من', 'يحتوي',
        'يهدف', 'تسعى', 'هدفها', 'مهمتها',
        'يتميز', 'تتميز', 'خصائص', 'صفات',
        'أنواع', 'أقسام', 'تصنيفات', 'تنقسم',
        'أسباب', 'عوامل', 'مؤثرات',
        'نتائج', 'آثار', 'تأثيرات',
        'مراحل', 'خطوات', 'عمليات',
        'أهمية', 'فوائد', 'مزايا',
        'تحديات', 'مشاكل', 'صعوبات',
        'استراتيجيات', 'أساليب', 'طرق', 'وسائل',
        'مبادئ', 'أسس', 'قواعد'
    ]
    
    # تقسيم النص إلى جمل
    sentences = re.split(r'[.!?;:\n]', text)
    
    # إزالة الجمل الفارغة والقصيرة
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    
    # استخراج الجمل المهمة
    important_sentences = []
    for sentence in sentences:
        # التحقق من وجود كلمات مفتاحية
        has_keyword = any(keyword in sentence for keyword in keywords)
        
        # التحقق من طول الجملة
        is_long_enough = len(sentence) > 30
        
        # التحقق من أنها ليست مجرد أرقام أو رموز
        is_meaningful = len(re.findall(r'[أ-يa-zA-Z]', sentence)) > 10
        
        if (has_keyword or is_long_enough) and is_meaningful:
            important_sentences.append(sentence)
    
    # إزالة التكرارات
    important_sentences = list(dict.fromkeys(important_sentences))
    
    # تحويل الجمل المهمة إلى أسئلة
    for i, sentence in enumerate(important_sentences[:50], 1):  # حد أقصى 50 سؤال
        # تنظيف الجملة
        sentence = sentence.strip()
        
        # تحويل الجملة إلى سؤال
        question_text = sentence
        
        # إضافة علامة استفهام إذا لم تكن موجودة
        if not question_text.endswith('؟'):
            # محاولة تحويل الجملة إلى سؤال
            if 'هو' in question_text or 'تعتبر' in question_text:
                question_text = question_text.replace('هو', 'ما هو')
                question_text = question_text.replace('تعتبر', 'ما هي')
            elif 'يتميز' in question_text:
                question_text = question_text.replace('يتميز', 'بماذا يتميز')
            elif 'أهمية' in question_text:
                question_text = question_text.replace('أهمية', 'ما أهمية')
            elif 'أنواع' in question_text:
                question_text = question_text.replace('أنواع', 'ما هي أنواع')
            elif 'مراحل' in question_text:
                question_text = question_text.replace('مراحل', 'ما هي مراحل')
            elif 'أسباب' in question_text:
                question_text = question_text.replace('أسباب', 'ما هي أسباب')
            
            question_text += "؟"
        
        # تحديد مستوى الصعوبة
        level = determine_difficulty_level(sentence)
        
        questions.append({
            "id": i,
            "level": level,
            "text": question_text,
            "original_sentence": sentence[:100] + "..." if len(sentence) > 100 else sentence
        })
    
    # إذا لم يتم العثور على أسئلة، قم باستخراج جمل عشوائية
    if len(questions) == 0:
        for i, sentence in enumerate(sentences[:20], 1):
            if len(sentence) > 30:
                questions.append({
                    "id": i,
                    "level": "بسيط",
                    "text": f"ما هي المعلومات الرئيسية حول: {sentence[:50]}...؟",
                    "original_sentence": sentence[:100] + "..." if len(sentence) > 100 else sentence
                })
    
    return questions

# دالة تحديد مستوى الصعوبة
def determine_difficulty_level(sentence):
    # كلمات للمستوى المتقدم
    advanced_keywords = [
        'تحليل', 'تقييم', 'نقد', 'استراتيجي', 'معقد', 'نظريات',
        'تطبيقات', 'مقارنة', 'التحوط', 'الاستراتيجي', 'متقدم'
    ]
    
    # كلمات للمستوى المتوسط
    medium_keywords = [
        'بسبب', 'بينما', 'الفجوة', 'علاقة', 'تأثير', 'نتيجة',
        'عوامل', 'مؤشرات', 'آليات', 'عمليات', 'مراحل'
    ]
    
    # حساب عدد الكلمات المفتاحية
    advanced_count = sum(1 for kw in advanced_keywords if kw in sentence)
    medium_count = sum(1 for kw in medium_keywords if kw in sentence)
    
    # تحديد المستوى
    if advanced_count >= 2:
        return "متقدم"
    elif advanced_count >= 1 or medium_count >= 2:
        return "متوسط"
    else:
        return "بسيط"

# دالة استخراج النص من PDF مع معالجة أفضل
def extract_text_from_pdf(uploaded_file):
    try:
        # قراءة محتوى الملف
        pdf_bytes = uploaded_file.read()
        # فتح ملف PDF
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        full_text = ""
        pages_text = []
        
        # استخراج النص من كل صفحة
        for page_num in range(len(doc)):
            page = doc[page_num]
            page_text = page.get_text()
            
            # تنظيف النص
            page_text = page_text.replace('\n', ' ')
            page_text = re.sub(r'\s+', ' ', page_text)
            
            pages_text.append({
                'number': page_num + 1,
                'text': page_text
            })
            
            full_text += f"\n--- صفحة {page_num + 1} ---\n{page_text}"
        
        # إحصائيات عن الملف
        stats = {
            'total_pages': len(doc),
            'total_chars': len(full_text),
            'pages_text': pages_text
        }
        
        return full_text, stats
    except Exception as e:
        st.error(f"حدث خطأ في معالجة ملف PDF: {str(e)}")
        return None, None

# دالة تصدير الأسئلة إلى Word مع تنسيق أفضل
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
        
        # إضافة خيارات متقدمة
        with st.expander("⚙️ خيارات متقدمة"):
            max_questions = st.slider("الحد الأقصى لعدد الأسئلة", 5, 50, 30)
            difficulty_filter = st.multiselect(
                "مستويات الصعوبة",
                ["بسيط", "متوسط", "متقدم"],
                default=["بسيط", "متوسط", "متقدم"]
            )
        
        if uploaded_file:
            st.success(f"✅ تم رفع الملف: {uploaded_file.name}")
            
            # عرض معلومات الملف
            file_details = {
                "اسم الملف": uploaded_file.name,
                "نوع الملف": uploaded_file.type,
                "الحجم": f"{uploaded_file.size / 1024:.2f} KB"
            }
            st.json(file_details)
            
            # زر لبدء المعالجة
            if st.button("🚀 استخراج الأسئلة", type="primary", use_container_width=True):
                with st.spinner("جاري معالجة الملف واستخراج الأسئلة..."):
                    # استخراج النص من PDF
                    full_text, stats = extract_text_from_pdf(uploaded_file)
                    
                    if full_text and stats:
                        # عرض إحصائيات الملف
                        st.info(f"📊 تم استخراج {stats['total_pages']} صفحة، {stats['total_chars']} حرف")
                        
                        # استخراج الأسئلة
                        all_questions = extract_questions_from_pdf(full_text)
                        
                        # تطبيق الفلتر حسب المستوى
                        questions = [q for q in all_questions if q['level'] in difficulty_filter]
                        questions = questions[:max_questions]
                        
                        if questions:
                            # حفظ الأسئلة في session state
                            st.session_state.questions = questions
                            st.session_state.full_text = full_text
                            st.session_state.stats = stats
                            st.success(f"✅ تم استخراج {len(questions)} سؤالاً بنجاح!")
                            st.balloons()
                        else:
                            st.warning("⚠️ لم يتم العثور على أسئلة في الملف. حاول رفع ملف آخر.")
                            # عرض جزء من النص للمساعدة في التشخيص
                            with st.expander("🔍 معاينة النص المستخرج"):
                                st.text(full_text[:500])
    
    with col2:
        st.markdown("### 📋 الأسئلة المستخرجة")
        
        # عرض الأسئلة إذا كانت موجودة في session state
        if 'questions' in st.session_state and st.session_state.questions:
            questions = st.session_state.questions
            
            # إحصائيات سريعة
            levels_count = {}
            for q in questions:
                level = q['level']
                levels_count[level] = levels_count.get(level, 0) + 1
            
            # عرض الإحصائيات
            col_stats1, col_stats2, col_stats3, col_stats4 = st.columns(4)
            with col_stats1:
                st.metric("📊 إجمالي الأسئلة", len(questions))
            with col_stats2:
                st.metric("🟢 بسيط", levels_count.get('بسيط', 0))
            with col_stats3:
                st.metric("🟡 متوسط", levels_count.get('متوسط', 0))
            with col_stats4:
                st.metric("🔴 متقدم", levels_count.get('متقدم', 0))
            
            # عرض الأسئلة في tab
            tab1, tab2, tab3 = st.tabs(["📝 عرض الأسئلة", "🔧 خيارات التصدير", "📊 إحصائيات"])
            
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
                                <p style="margin-top: 10px; font-size: 16px;">{q['text']}</p>
                                <details style="margin-top: 10px; font-size: 12px; color: #666;">
                                    <summary>معاينة النص الأصلي</summary>
                                    <p>{q.get('original_sentence', '')}</p>
                                </details>
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
            
            with tab3:
                st.markdown("#### 📊 إحصائيات وتحليلات")
                
                # توزيع الأسئلة حسب المستوى
                levels_data = {
                    'بسيط': levels_count.get('بسيط', 0),
                    'متوسط': levels_count.get('متوسط', 0),
                    'متقدم': levels_count.get('متقدم', 0)
                }
                st.bar_chart(levels_data)
                
                # معلومات عن الملف
                if 'stats' in st.session_state:
                    st.markdown("#### 📄 معلومات الملف")
                    st.write(f"- عدد الصفحات: {st.session_state.stats['total_pages']}")
                    st.write(f"- عدد الأحرف: {st.session_state.stats['total_chars']:,}")
                
                # معاينة النص الكامل
                with st.expander("📄 عرض النص الكامل المستخرج"):
                    st.text_area("النص الكامل:", st.session_state.full_text, height=300, disabled=True)
        else:
            st.info("💡 قم برفع ملف PDF واضغط على زر 'استخراج الأسئلة' لعرض الأسئلة هنا")
    
    # شريط جانبي مع معلومات إضافية
    with st.sidebar:
        st.markdown("### ℹ️ معلومات عن التطبيق")
        st.markdown("""
        **كيف يعمل التطبيق؟**
        
        1. **استخراج النص**: يقوم التطبيق باستخراج النص من ملف PDF
        2. **تحليل المحتوى**: يبحث عن الجمل الغنية بالمعلومات والكلمات المفتاحية
        3. **تحويل إلى أسئلة**: يحول الجمل المهمة إلى أسئلة تعليمية
        4. **تصنيف المستوى**: يصنف الأسئلة حسب الصعوبة
        
        **مستويات الصعوبة:**
        - 🟢 **بسيط**: أسئلة أساسية عن التعريفات والمفاهيم
        - 🟡 **متوسط**: أسئلة عن الأسباب والنتائج والعلاقات
        - 🔴 **متقدم**: أسئلة تحليلية واستراتيجية معقدة
        
        **الكلمات المفتاحية التي يبحث عنها:**
        - التعريفات: يعرف، هو، تعتبر
        - المحتوى: يتكون، يشمل، يحتوي
        - الأهداف: يهدف، تسعى
        - التصنيفات: أنواع، أقسام
        - التحليل: أسباب، نتائج، تأثيرات
        
        **نصائح للحصول على أفضل النتائج:**
        - استخدم ملفات PDF نصية (غير ممسوحة ضوئياً)
        - كلما كان المحتوى أكثر تنظيماً، كانت الأسئلة أفضل
        - يمكن تعديل عدد الأسئلة في الخيارات المتقدمة
        """)
        
        st.markdown("---")
        st.markdown("### 🛠️ التقنيات المستخدمة")
        st.markdown("""
        - **Streamlit**: واجهة المستخدم التفاعلية
        - **PyMuPDF**: معالجة واستخراج النص من PDF
        - **python-docx**: إنشاء ملفات Word
        - **تعبيرات منتظمة (Regex)**: تحليل النص والبحث عن الأنماط
        """)

if __name__ == "__main__":
    main()
