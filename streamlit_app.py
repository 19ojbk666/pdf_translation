import streamlit as st
from function import trans_run

# st.set_page_config(page_title="PDf 翻译", page_icon="📊",layout="wide")
st.set_page_config(page_title="PDf 翻译", page_icon="📊")
st.title('PDF 翻译')

ss = st.session_state

with st.form(f'请输入参数'):
    ss.APP_KEY = st.text_input("APP_KEY 应用ID")
    ss.APP_SECRET = st.text_input("APP_SECRET 应用密钥")
    ss.pdf_path = st.text_input("所翻译的文件夹路径", value = "C:/fanyi_source_folder")
    ss.trans_tpye = st.selectbox("翻译类型",  ['中译韩', '韩译中', '中译英', '英译中','英译韩','韩译英'], index=0)
    submitted = st.form_submit_button('开始翻译')
    if ss.trans_tpye == "中译韩" :
        ss.lang_from = 'zh-CHS'
        ss.lang_to = 'ko'
    elif ss.trans_tpye == "韩译中":
        ss.lang_from = 'ko'
        ss.lang_to = 'zh-CHS'
    elif ss.trans_tpye == "中译英":
        ss.lang_from = 'zh-CHS'
        ss.lang_to = 'en'
    elif ss.trans_tpye == "英译中":
        ss.lang_from = 'en'
        ss.lang_to = 'zh-CHS'
    elif ss.trans_tpye == "英译韩":
        ss.lang_from = 'en'
        ss.lang_to = 'ko'
    elif ss.trans_tpye == "韩译英":
        ss.lang_from = 'ko'
        ss.lang_to = 'en'
if submitted:
    trans_run(ss.pdf_path, ss.APP_KEY, ss.APP_SECRET, ss.lang_from, ss.lang_to)