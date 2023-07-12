import os
import numpy as np
import streamlit as st
import fitz
import cv2
import zipfile


st.title("PDF to PNG")

file = st.file_uploader("请上传PDF")
if file is not None:
    doc = fitz.open(stream=file.read(), filetype="pdf")
    for i in range(len(doc)):
            page = doc.load_page(i)
            pix = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72), dpi=300)
            img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape((pix.height, pix.width, pix.n))
            st.image(img_array, caption=f"Page {i+1}", use_column_width=True)
            st.download_button(label='Download image',data=img_array, file_name=f"{i+1}.png",mime="image/jpeg")

