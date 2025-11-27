import google.generativeai as genai
import os

# Paste your API Key here
GENAI_API_KEY = 'AIzaSyAhZAohldiji5fROjixsmtnEylSzSoNCMY'
genai.configure(api_key=GENAI_API_KEY)

print("Listing available models...")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)