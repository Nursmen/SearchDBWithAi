from fastapi import FastAPI, File, UploadFile, HTTPException
import fitz 
import pandas as pd

def read_pdf(file_path):
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def read_csv(file_path):
    df = pd.read_csv(file_path)
    return df.to_string(index=False)

def read_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()
    
def read_excel(file_path):
    df = pd.read_excel(file_path)
    return df.to_string(index=False)