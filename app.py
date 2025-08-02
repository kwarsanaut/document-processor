import streamlit as st
import tempfile
import os
import docx
import openai
import pandas as pd
import re
from datetime import datetime

st.set_page_config(page_title="AI Document Processor", page_icon="🤖", layout="wide")

# Initialize session state
if 'processed_docs' not in st.session_state:
    st.session_state.processed_docs = []

st.title("🤖 AI Document Processor")
st.caption("Upload and process documents with AI")

# Sidebar
with st.sidebar:
    st.header("Settings")
    openai_key = st.text_input("OpenAI API Key", type="password")
    if openai_key:
        openai.api_key = openai_key
        st.success("API key set!")

# Main interface
uploaded_file = st.file_uploader("Choose a document", type=['docx', 'txt'])

if uploaded_file is not None:
    st.info(f"File: {uploaded_file.name} ({uploaded_file.size:,} bytes)")
    
    if st.button("🚀 Process Document"):
        with st.spinner("Processing..."):
            try:
                # Save file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_file_path = tmp_file.name
                
                # Extract content
                content = ""
                if uploaded_file.name.endswith('.docx'):
                    doc = docx.Document(tmp_file_path)
                    content = '\n'.join([para.text for para in doc.paragraphs if para.text.strip()])
                elif uploaded_file.name.endswith('.txt'):
                    content = uploaded_file.getvalue().decode('utf-8')
                
                # Clean up
                os.unlink(tmp_file_path)
                
                if content:
                    st.success("✅ Document processed!")
                    
                    # Show content
                    st.subheader("📝 Extracted Content")
                    st.text_area("Content", content, height=200)
                    
                    # Extract basic patterns
                    st.subheader("🔍 Found Patterns")
                    
                    # Indonesian phone numbers
                    phones = re.findall(r'(\+62|08)\d{2,3}[-\s]?\d{3,4}[-\s]?\d{3,4}', content)
                    if phones:
                        st.write("📞 Phone Numbers:", phones)
                    
                    # Email addresses
                    emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', content)
                    if emails:
                        st.write("📧 Email Addresses:", emails)
                    
                    # Currency
                    currency = re.findall(r'Rp\.?\s?[\d.,]+|IDR\s?[\d.,]+', content)
                    if currency:
                        st.write("💰 Currency Amounts:", currency)
                    
                    # Dates
                    dates = re.findall(r'\d{1,2}[/-]\d{1,2}[/-]\d{4}|\d{4}-\d{2}-\d{2}', content)
                    if dates:
                        st.write("📅 Dates:", dates)
                    
                    # AI Summary (if API key provided)
                    if openai_key:
                        st.subheader("🤖 AI Summary")
                        try:
                            response = openai.ChatCompletion.create(
                                model="gpt-3.5-turbo",
                                messages=[{
                                    "role": "user", 
                                    "content": f"Summarize this Indonesian business document in 2-3 sentences:\n\n{content[:1000]}"
                                }],
                                max_tokens=150
                            )
                            summary = response.choices[0].message.content
                            st.info(summary)
                        except Exception as e:
                            st.error(f"AI summary failed: {e}")
                    
                    # Save to session
                    st.session_state.processed_docs.append({
                        'filename': uploaded_file.name,
                        'content': content,
                        'processed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                    
                else:
                    st.error("No content extracted from document")
                    
            except Exception as e:
                st.error(f"Processing failed: {str(e)}")

# Show processed documents
if st.session_state.processed_docs:
    st.subheader("📁 Processed Documents")
    for i, doc in enumerate(st.session_state.processed_docs):
        with st.expander(f"{doc['filename']} - {doc['processed_at']}"):
            st.text_area(f"Content {i}", doc['content'], height=100, key=f"content_{i}")

# Statistics
if st.session_state.processed_docs:
    st.subheader("📊 Statistics")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Documents Processed", len(st.session_state.processed_docs))
    with col2:
        total_chars = sum(len(doc['content']) for doc in st.session_state.processed_docs)
        st.metric("Total Characters", f"{total_chars:,}")

# Footer
st.markdown("---")
st.markdown("🤖 AI Document Processor | Simple & Fast")
