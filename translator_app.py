import streamlit as st
from googletrans import Translator, LANGUAGES
import requests
from bs4 import BeautifulSoup
import docx2txt
import ssl

# 禁用证书验证
ssl._create_default_https_context = ssl._create_unverified_context

def translate_text(text, source_lang, target_lang):
    translator = Translator()
    if source_lang == "auto":
        translated = translator.translate(text, dest=target_lang)
        detected_lang = translated.src
    else:
        translated = translator.translate(text, src=source_lang, dest=target_lang)
        detected_lang = source_lang
    return translated.text, detected_lang

# 定义支持的所有语言
SUPPORTED_LANGUAGES = LANGUAGES

# 定义下拉菜单中显示的语言
MENU_LANGUAGES = {
    'zh-cn': '中文（简体）',
    'en': 'English'
}

def get_language_code(language_name):
    return next((code for code, name in MENU_LANGUAGES.items() if name == language_name), None)

def get_language_name(lang_code):
    return SUPPORTED_LANGUAGES.get(lang_code, '未知')

def extract_text_from_website(url):
    try:
        response = requests.get(url, verify=False)  # 禁用证书验证
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.get_text()
    except Exception as e:
        st.error(f"提取网站内容时出错: {str(e)}")
        return "提取网站内容失败"

def translate_callback():
    if st.session_state.input_text:
        translated_text, detected_lang = translate_text(st.session_state.input_text, st.session_state.source_lang_code, st.session_state.target_lang_code)
        st.session_state.translated_text = translated_text
        st.session_state.detected_lang = detected_lang

def clear_input():
    st.session_state.input_text = ""
    st.session_state.translated_text = ""

def swap_languages():
    st.session_state.source_lang, st.session_state.target_lang = st.session_state.target_lang, st.session_state.source_lang
    st.session_state.source_lang_code, st.session_state.target_lang_code = st.session_state.target_lang_code, st.session_state.source_lang_code
    if st.session_state.input_text:
        st.session_state.input_text, st.session_state.translated_text = st.session_state.translated_text, st.session_state.input_text

st.set_page_config(layout="wide", page_title="多功能翻译工具")
st.title("多功能翻译工具")

# 创建选项卡
tab1, tab2, tab3 = st.tabs(["文字", "文档", "网站"])

with tab1:
    col1, col2 = st.columns(2)

    with col1:
        if 'source_lang' not in st.session_state:
            st.session_state.source_lang = 'English'
            st.session_state.source_lang_code = 'en'
        
        source_lang = st.selectbox("源语言:", ["自动检测"] + list(MENU_LANGUAGES.values()), key="source_lang", index=2)  # 默认选择英语
        st.session_state.source_lang_code = "auto" if source_lang == "自动检测" else get_language_code(source_lang)
        
        st.text_area("在此输入文本", height=200, key="input_text", on_change=translate_callback)
        
        st.button("清空", on_click=clear_input)

    with col2:
        if 'target_lang' not in st.session_state:
            st.session_state.target_lang = '中文（简体）'
            st.session_state.target_lang_code = 'zh-cn'
        
        target_lang = st.selectbox("目标语言:", list(MENU_LANGUAGES.values()), key="target_lang", index=0)  # 默认选择中文
        st.session_state.target_lang_code = get_language_code(target_lang)
        
        if 'translated_text' not in st.session_state:
            st.session_state.translated_text = ""
        st.text_area("翻译结果", value=st.session_state.translated_text, height=200, key="translated_text_display", disabled=True)
        
        col2_1, col2_2 = st.columns(2)
        with col2_1:
            st.button("翻译", on_click=translate_callback)
        with col2_2:
            st.button("转换", on_click=swap_languages)

    if st.session_state.translated_text and 'detected_lang' in st.session_state:
        detected_lang_name = get_language_name(st.session_state.detected_lang)
        st.info(f"检测到的源语言: {detected_lang_name}")

with tab2:
    uploaded_file = st.file_uploader("上传文档", type=["txt", "docx"])
    if uploaded_file is not None:
        if uploaded_file.type == "text/plain":
            file_contents = uploaded_file.getvalue().decode("utf-8")
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            file_contents = docx2txt.process(uploaded_file)
        st.text_area("文档内容", value=file_contents, height=150)
        
        doc_target_lang = st.selectbox("选择目标语言:", list(MENU_LANGUAGES.values()), key="doc_target_lang")
        doc_target_lang_code = get_language_code(doc_target_lang)
        
        if st.button("翻译文档内容"):
            translated_text, detected_lang = translate_text(file_contents, "auto", doc_target_lang_code)
            st.text_area("翻译结果", value=translated_text, height=150)
            st.info(f"检测到的源语言: {get_language_name(detected_lang)}")

with tab3:
    website_url = st.text_input("输入网站URL")
    
    web_target_lang = st.selectbox("选择目标语言:", list(MENU_LANGUAGES.values()), key="web_target_lang")
    web_target_lang_code = get_language_code(web_target_lang)
    
    if st.button("提取并翻译网站内容"):
        if website_url:
            try:
                website_text = extract_text_from_website(website_url)
                st.text_area("提取的文本", value=website_text, height=150)
                translated_text, detected_lang = translate_text(website_text, "auto", web_target_lang_code)
                st.text_area("翻译结果", value=translated_text, height=150)
                st.info(f"检测到的源语言: {get_language_name(detected_lang)}")
            except Exception as e:
                st.error(f"提取网站内容时出错: {str(e)}")
        else:
            st.warning("请输入有效的网站URL")

st.markdown("---")
st.write("注: 本工具使用Google翻译API进行翻译。")

# 添加开发者信息
st.markdown("---")
st.write("开发者: Huaiyuan Tan")
st.write("© 2024 保留所有权利")