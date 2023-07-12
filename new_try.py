import os
import numpy as np
import streamlit as st
import fitz
import cv2
import zipfile

def extract_report(pdf_path,file_name,book_title,dpi=300,contour_area_val=100000,size_val=10000):
    final_pictures=[]
    final_names=[]
    doc = fitz.open(stream=file_name.read(), filetype="pdf")
    for page_index in range(len(doc)):
        page = doc.load_page(page_index)
        pix = page.get_pixmap(matrix=fitz.Matrix(dpi/72, dpi/72), dpi=dpi)
        img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape((pix.height, pix.width, pix.n))
        img = img_array
        # 转为灰度图
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # 二值化
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
        #膨胀算法连接轮廓
        kernel = np.ones((3, 3), np.uint8)
        dilated = cv2.dilate(thresh, kernel, iterations=2)
        #把噪声过滤掉
        data=np.array(dilated, dtype= bool)
        rem = morphology.remove_small_objects(data, 15000,connectivity=1)
        binary_image = np.uint8(rem) * 255
        #膨胀算法连接轮廓
        kernel = np.ones((3, 3), np.uint8)
        dilated_2 = cv2.dilate(binary_image, kernel, iterations=3)
        #####创建全填充的完整图
        mask = dilated_2.copy()
        contours, hierarchy = cv2.findContours(dilated_2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        valid = len(contours) > 0
        for k in range(len(contours)):
           mask = cv2.drawContours(mask, contours, k, 255, cv2.FILLED)
        # 定义结构元素（核）大小
        kernel_size = (3, 3)
        # 创建结构元素
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, kernel_size)
        # 执行闭操作
        closed_image = cv2.morphologyEx(dilated_2, cv2.MORPH_CLOSE, kernel)
        #加入分水岭算法来打断连接
        # Canny边缘检测
        edges = cv2.Canny(closed_image, 100, 200)
        # 轮廓检测
        raw_contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours=[]
        for i in raw_contours:
          area=cv2.contourArea(i)
          if area>contour_area_val:
            contours.append(i)
          else:
            continue
        # 根据轮廓将每个样本切割出来并保存
        for i in range(len(contours)):
            x, y, w, h = cv2.boundingRect(contours[i])
            raw_sample = cv2.bitwise_not(thresh[y:y+h, x:x+w])
            sample = mask[y:y+h, x:x+w]
            height, width = raw_sample.shape[:2]
            if height*width>size_val:
            #这里开始写基于填充后的轮廓如何判定他是不是完整器物
              final_pictures.append(raw_sample)
              final_names.append(f'{book_title}_{page_index}_{i}')
            else:
              continue
    return dict(zip(final_names,final_pictures))


def save_arrays_to_zip(arrays, zip_file_path):
    with zipfile.ZipFile(zip_file_path, mode='w') as zip_file:
        for key, image in arrays:
            cv2.imwrite(f'{key}.png',image)
            zip_file.write(f'{key}.png')
            os.remove(f'{key}.png')


############start##################
st.title("PDF to PNG")

file_name = st.file_uploader("请上传PDF")
book_title = st.text_input("输入pdf编号")

if file_name is not None:
    img_dict=extract_report(pdf_path,file_name,book_title)
    img_list=list(img_dict.values())
    for i in range(len(img_list)):
        st.image(img_list[i], caption=f"Page {i+1}", use_column_width=False)
    save_arrays_to_zip(img_dict, 'output.zip')
    with open('output.zip', 'rb') as f:
      result = f.read()
      st.download_button(
          label='Download output.zip',
          data=result,
          file_name='output.zip',
          mime='application/zip'
      )
