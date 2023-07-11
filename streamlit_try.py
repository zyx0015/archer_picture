import os
import numpy as np
import streamlit as st
import fitz
import cv2

st.title("PDF to PNG")

file = st.file_uploader("请上传PDF")
if file is not None:
    doc = fitz.open(stream=file.read(), filetype="pdf")
    folder_name = st.text_input("Enter folder name")
    if folder_name:
        os.makedirs(folder_name, exist_ok=True)
        for i in range(len(doc)):
            page = doc.load_page(i)
            os.chdir('D:\\数据库training')
            pix = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72), dpi=300)
            img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape((pix.height, pix.width, pix.n))
            cv2.imwrite(f'{folder_name}/{i+1}.png', img_array)
            st.image(img_array, caption=f"Page {i+1}", use_column_width=True)
