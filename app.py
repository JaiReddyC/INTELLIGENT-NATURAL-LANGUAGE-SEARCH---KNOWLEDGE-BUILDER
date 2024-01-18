 app.py
import streamlit as st
import spacy
from transformers import BartForConditionalGeneration, BartTokenizer
import pptx
import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
from pptx import Presentation
from docx import Document
import PyPDF2
from data_generators import *
from models import *

def main():
    st.title("Knowledge Builder")
    page = st.sidebar.selectbox("Choose a page", ["Home", "Use my file"])
    if page == "Home":
        st.header("Work Based on PPTs & Web sites and Reports")
        # st.subheader("Available Source Files:")
        # source_files = ["ambroxol.pptx", "Cancer.pptx", "approach-to-fever.pptx", "Know-Everything-About-Ast.pptx"]
        # for file in source_files:
        #     st.write(file)
        # st.write("R&D Reports ")
        expand_files = st.expander("Available Source Files", expanded=False)
        with expand_files:
            st.write("Web-Site's of R&D Reports")
            source_files = ["ambroxol.pptx", "Cancer.pptx", "approach-to-fever.pptx", "Know-Everything-About-Ast.pptx"]
            for file in source_files:
                st.write(file)
        query = st.text_input("Enter your query:")
        if st.button("Search"):
            with st.spinner("Searching..."):
                text_from_ppt = ""
                cache_file = "webpage_cache.txt"
                if os.path.exists(cache_file):
                    # If the cached file exists, load text from the file
                    with open(cache_file, 'r', encoding='utf-8') as file:
                        text_from_ppt += file.read()
                else:
                    links_df = pd.read_csv("therapy.csv")
                    for index, row in links_df.iterrows():
                        document_id = row['document_id']
                        topic = row['topic']
                        link = row['link']
                        class_type = row['class_type']
                        if "slideshare" in link:
                            #print("from ppts")
                            text_from_ppt += extract_text_from_ppt(link)
                        else:  # Assuming web page or other source types
                            #print("from webpages")
                            text_from_ppt += extract_text_from_webpage(link)
                ppts_file_paths = ("ambroxol.pptx", "Cancer.pptx", "approach-to-fever.pptx", "Know-Everything-About-Ast.pptx")
                for ppt_path in ppts_file_paths:
                    text_from_ppt += extract_text_from_ppt(ppt_path)
                nlp = spacy.load("en_core_web_sm")
                doc = nlp(text_from_ppt)
                knowledge_graph = {}
                for entity in doc.ents:
                    if entity.label_:
                        knowledge_graph[entity.text] = {
                            'label': entity.label_,
                            'text': entity.sent.text
                        }
                tokenizer = BartTokenizer.from_pretrained("facebook/bart-base")
                model = BartForConditionalGeneration.from_pretrained("facebook/bart-base")

                results = search_knowledge_graph(query, knowledge_graph)
                response = generate_response(results, model, tokenizer,250)
                decoded_response = tokenizer.decode(response[0], skip_special_tokens=True)

                cleaned_response = ' '.join(filter(lambda x: x[:2] != '>>' and x.isalnum() and len(x) <= 10, decoded_response.split()))

                if cleaned_response == "Based on your what I found in the knowledge":
                    st.error("No information found based on your query. Please try another query.")
                else:
                    st.success(f"Response: {query}")
                    st.success(f"        Based on your query, here's what I found in the knowledge graph -> \n  {cleaned_response}")
    elif page == "Use my file":
        st.header("Your own data")
        uploaded_files = st.file_uploader("Upload PPT or PDF files", accept_multiple_files=True)
        query = st.text_input("Enter your query:")
        if uploaded_files:
            if st.button("Search"):
                with st.spinner("Searching..."):
                    all_text_from_files = ""  # To accumulate text from all uploaded files
                    for uploaded_file in uploaded_files:
                        file_ext = uploaded_file.name.split(".")[-1].lower()
                        if file_ext == "pptx":
                            text_from_file = extract_text_from_ppt(uploaded_file)
                        elif file_ext == "pdf":
                            text_from_file = extract_text_from_pdf(uploaded_file)
                        elif file_ext == "docx":
                            text_from_file = extract_text_from_docx(uploaded_file)
                        else:
                            st.error(f"Invalid file format for file '{uploaded_file.name}'. Please upload a PPT, PDF, or DOCX file.")
                            continue  # Move to the next file if the format is incorrect
                        # Accumulate text from all uploaded files
                        all_text_from_files += text_from_file
                    nlp = spacy.load("en_core_web_sm")
                    doc = nlp(all_text_from_files)
                    knowledge_graph = {}
                    for entity in doc.ents:
                        if entity.label_:
                            knowledge_graph[entity.text] = {
                                'label': entity.label_,
                                'text': entity.sent.text
                            }
                    results = search_knowledge_graph(query, knowledge_graph)
                    tokenizer = BartTokenizer.from_pretrained("facebook/bart-base")
                    model = BartForConditionalGeneration.from_pretrained("facebook/bart-base")
                    response = generate_response(results, model, tokenizer,500)
                    decoded_response = tokenizer.decode(response[0], skip_special_tokens=True)
                    cleaned_response = ' '.join(filter(lambda x: x[:2] != '>>' and x.isalnum() and len(x) <= 10, decoded_response.split()))
                    if cleaned_response == "Based on your what I found in the knowledge":
                        st.error("No information found based on your query. Please try another query.")
                    else:
                        st.success(f"Response: {query}")
                        st.success(f"        Based on your query, here's what I found in the knowledge graph -> \n  {cleaned_response}")

if _name_ == "_main_":
    main()
