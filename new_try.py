import os
import numpy as np
import streamlit as st
import cv2

def read_images_from_folder(folder_path):
    images = []
    for filename in os.listdir(folder_path):
        img = cv2.imread(os.path.join(folder_path,filename))
        if img is not None:
            images.append(img)
    return images

st.title("PDF to PNG")

file = st.file_uploader("请上传PDF")
if file is not None:
    doc = fitz.open(stream=file.read(), filetype="pdf")
    work_path = st.text_input("Enter work path")
    folder_name = st.text_input("Enter folder name")
    if folder_name:
        os.makedirs(folder_name, exist_ok=True)
        img_list=read_images_from_folder("test_png")
        for img in range(len(img_list)):
            page = doc.load_page(i)
            cv2.imwrite(f'{folder_name}/{i+1}.png', img)
            st.image(img_array, caption=f"Page {i+1}", use_column_width=True)
