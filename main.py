import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import pdfplumber
import spacy
import re
from datetime import datetime

    # Load NLP model
nlp = spacy.load("en_core_web_sm")

    # Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
        text = ""
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text

    # Function to extract dates from text
def extract_dates(text):
        date_pattern = r'\d{1,2}/\d{1,2}/\d{4}|\d{1,2}-\d{1,2}-\d{4}|\d{4}-\d{1,2}-\d{1,2}'
        dates = re.findall(date_pattern, text)
        return [datetime.strptime(date, '%m/%d/%Y') for date in dates]

    # Function to perform NER
def perform_ner(text):
        doc = nlp(text)
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        return entities

    # Function to identify potential causes of action
def identify_causes_of_action(text):
        causes = []
        keywords = {
            "Negligence": ["negligence", "duty of care", "breach", "damages"],
            "Breach of Contract": ["breach of contract", "agreement", "violation"],
            "Defamation": ["defamation", "libel", "slander", "reputation"],
        }
        for cause, words in keywords.items():
            if any(word in text.lower() for word in words):
                causes.append(cause)
        return causes

    # Main Streamlit app
def main():
        st.title("Legal Case Analysis MVP")

        # Sidebar navigation
        page = st.sidebar.selectbox("Choose a page",
                                     [
            "Document Upload", 
            "Timeline", 
            "Entity Recognition", 
            "Cause of Action", 
            "Risk Assessment", 
            "Witness Management", 
            "Deposition Prep", 
            "Trial Presentation"
        ])

        if page == "Document Upload":
            st.header("Document Upload and Analysis")
            uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
            if uploaded_file is not None:
                text = extract_text_from_pdf(uploaded_file)
                st.text_area("Extracted Text", text, height=300)
                st.session_state['text'] = text

        elif page == "Timeline":
            st.header("Timeline Generation")
            if 'text' in st.session_state:
                dates = extract_dates(st.session_state['text'])
                df = pd.DataFrame({'dates': dates})
                st.line_chart(df.groupby('dates').size())
            else:
                st.write("Please upload a document first.")

        elif page == "Entity Recognition":
            st.header("Named Entity Recognition")
            if 'text' in st.session_state:
                entities = perform_ner(st.session_state['text'])
                df = pd.DataFrame(entities, columns=['Entity', 'Type'])
                st.dataframe(df)
            else:
                st.write("Please upload a document first.")

        elif page == "Cause of Action":
            st.header("Cause of Action Analysis")
            if 'text' in st.session_state:
                causes = identify_causes_of_action(st.session_state['text'])
                for cause in causes:
                    st.write(f"- {cause}")
            else:
                st.write("Please upload a document first.")

        elif page == "Risk Assessment":
            st.header("Risk Assessment")
            st.write("This is a simplified risk assessment. "
                     "In a real application, this would be more comprehensive.")
            strength = st.slider("Case Strength (1-10)", 1, 10, 5)
            complexity = st.slider("Case Complexity (1-10)", 1, 10, 5)
            opposing_strength = st.slider("Opposing Party Strength (1-10)", 1, 10, 5)
            risk_score = (11 - strength) * complexity * opposing_strength / 10
            st.write(f"Estimated Risk Score: {risk_score:.2f}")

        elif page == "Witness Management":
            st.header("Witness Management")
            witness_name = st.text_input("Witness Name")
            witness_role = st.text_input("Witness Role")
            if st.button("Add Witness"):
                if 'witnesses' not in st.session_state:
                    st.session_state['witnesses'] = []
                st.session_state['witnesses'].append((witness_name, witness_role))
            if 'witnesses' in st.session_state:
                st.table(st.session_state['witnesses'])

        elif page == "Deposition Prep":
            st.header("Deposition Preparation")
            if 'text' in st.session_state:
                st.write("Based on the document, consider asking about:")
                entities = perform_ner(st.session_state['text'])
                for entity, type in entities[:5]:  # Show top 5 entities
                    st.write(f"- {entity} ({type})")
            custom_question = st.text_input("Add a custom question")
            if st.button("Add Question"):
                if 'questions' not in st.session_state:
                    st.session_state['questions'] = []
                st.session_state['questions'].append(custom_question)
            if 'questions' in st.session_state:
                for q in st.session_state['questions']:
                    st.write(f"- {q}")

        elif page == "Trial Presentation":
            st.header("Trial Presentation")
            st.write("This would be a simple document viewer in the MVP.")
            if 'text' in st.session_state:
                st.text_area("Document Viewer", st.session_state['text'], height=300)
            else:
                st.write("Please upload a document first.")

if __name__ == "__main__":
        main()
