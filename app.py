import streamlit as st
import tempfile
import os
import json
from datetime import datetime
import pandas as pd
import plotly.express as px
from processor import DocumentProcessor
import time

# Page config
st.set_page_config(
    page_title="AI Document Processor",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'processed_docs' not in st.session_state:
    st.session_state.processed_docs = []
if 'processor' not in st.session_state:
    st.session_state.processor = DocumentProcessor()

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .entity-tag {
        background-color: #e7f3ff;
        border: 1px solid #b3d9ff;
        border-radius: 15px;
        padding: 0.3rem 0.8rem;
        margin: 0.2rem;
        display: inline-block;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🤖 AI Document Processor</h1>', unsafe_allow_html=True)
st.markdown("### *Enterprise-grade document processing for Indonesian businesses*")

# Sidebar
with st.sidebar:
    st.header("🎛️ Settings")
    
    # API Keys
    with st.expander("API Configuration", expanded=False):
        openai_key = st.text_input("OpenAI API Key", type="password", value=os.getenv("OPENAI_API_KEY", ""))
        pinecone_key = st.text_input("Pinecone API Key", type="password", value=os.getenv("PINECONE_API_KEY", ""))
        
        if st.button("Save API Keys"):
            if openai_key:
                os.environ["OPENAI_API_KEY"] = openai_key
                st.session_state.processor.set_openai_key(openai_key)
                st.success("API keys saved!")
    
    # Processing Options
    st.subheader("Processing Options")
    extract_entities = st.checkbox("Extract Entities", value=True)
    extract_tables = st.checkbox("Extract Tables", value=True)
    generate_summary = st.checkbox("Generate Summary", value=True)
    indonesian_mode = st.checkbox("Indonesian Optimization", value=True)
    
    # Statistics
    st.subheader("📊 Statistics")
    st.metric("Documents Processed", len(st.session_state.processed_docs))
    if st.session_state.processed_docs:
        avg_time = sum(doc.get('processing_time', 0) for doc in st.session_state.processed_docs) / len(st.session_state.processed_docs)
        st.metric("Avg Processing Time", f"{avg_time:.1f}s")

# Main tabs
tab1, tab2, tab3, tab4 = st.tabs(["📄 Process Document", "🔍 Search Documents", "📊 Analytics", "ℹ️ About"])

with tab1:
    st.header("Upload & Process Document")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Choose a document",
            type=['pdf', 'docx', 'doc', 'png', 'jpg', 'jpeg', 'tiff'],
            help="Supported formats: PDF, DOCX, Images"
        )
        
        if uploaded_file is not None:
            # File info
            st.info(f"📁 **File:** {uploaded_file.name} ({uploaded_file.size:,} bytes)")
            
            # Process button
            if st.button("🚀 Process Document", type="primary"):
                with st.spinner("Processing document... This may take a few moments."):
                    try:
                        # Save uploaded file temporarily
                        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                            tmp_file.write(uploaded_file.getvalue())
                            tmp_file_path = tmp_file.name
                        
                        # Process document
                        start_time = time.time()
                        result = st.session_state.processor.process_document(
                            tmp_file_path,
                            options={
                                'extract_entities': extract_entities,
                                'extract_tables': extract_tables,
                                'generate_summary': generate_summary,
                                'indonesian_mode': indonesian_mode
                            }
                        )
                        processing_time = time.time() - start_time
                        
                        # Clean up temp file
                        os.unlink(tmp_file_path)
                        
                        # Add to session state
                        doc_result = {
                            'filename': uploaded_file.name,
                            'processed_at': datetime.now().isoformat(),
                            'processing_time': processing_time,
                            'result': result
                        }
                        st.session_state.processed_docs.append(doc_result)
                        
                        # Display results
                        st.success("✅ Document processed successfully!")
                        
                        # Document info
                        st.subheader("📋 Document Information")
                        info_cols = st.columns(4)
                        with info_cols[0]:
                            st.metric("Type", result.get('classification', {}).get('category', 'Unknown'))
                        with info_cols[1]:
                            st.metric("Confidence", f"{result.get('classification', {}).get('confidence', 0):.1%}")
                        with info_cols[2]:
                            st.metric("Pages/Sections", result.get('metadata', {}).get('pages', 1))
                        with info_cols[3]:
                            st.metric("Processing Time", f"{processing_time:.1f}s")
                        
                        # Extracted content
                        if result.get('content'):
                            st.subheader("📝 Extracted Content")
                            with st.expander("View full content"):
                                st.text_area("Content", result['content'], height=300)
                        
                        # Entities
                        if extract_entities and result.get('entities'):
                            st.subheader("🏷️ Extracted Entities")
                            entities = result['entities']
                            
                            entity_cols = st.columns(2)
                            with entity_cols[0]:
                                if entities.get('people'):
                                    st.write("**👥 People:**")
                                    for person in entities['people']:
                                        st.markdown(f'<span class="entity-tag">👤 {person}</span>', unsafe_allow_html=True)
                                
                                if entities.get('organizations'):
                                    st.write("**🏢 Organizations:**")
                                    for org in entities['organizations']:
                                        st.markdown(f'<span class="entity-tag">🏢 {org}</span>', unsafe_allow_html=True)
                                
                                if entities.get('locations'):
                                    st.write("**📍 Locations:**")
                                    for loc in entities['locations']:
                                        st.markdown(f'<span class="entity-tag">📍 {loc}</span>', unsafe_allow_html=True)
                            
                            with entity_cols[1]:
                                if entities.get('dates'):
                                    st.write("**📅 Dates:**")
                                    for date in entities['dates']:
                                        st.markdown(f'<span class="entity-tag">📅 {date}</span>', unsafe_allow_html=True)
                                
                                if entities.get('monetary_amounts'):
                                    st.write("**💰 Amounts:**")
                                    for amount in entities['monetary_amounts']:
                                        st.markdown(f'<span class="entity-tag">💰 {amount}</span>', unsafe_allow_html=True)
                                
                                if entities.get('contact_info', {}).get('phones'):
                                    st.write("**📞 Phone Numbers:**")
                                    for phone in entities['contact_info']['phones']:
                                        st.markdown(f'<span class="entity-tag">📞 {phone}</span>', unsafe_allow_html=True)
                        
                        # Summary
                        if generate_summary and result.get('summary'):
                            st.subheader("📊 Document Summary")
                            summary = result['summary']
                            
                            if summary.get('executive_summary'):
                                st.info(f"**Executive Summary:** {summary['executive_summary']}")
                            
                            if summary.get('key_points'):
                                st.write("**Key Points:**")
                                for point in summary['key_points']:
                                    st.write(f"• {point}")
                            
                            if summary.get('urgency_level'):
                                urgency_color = {
                                    'LOW': 'green',
                                    'MEDIUM': 'orange', 
                                    'HIGH': 'red',
                                    'CRITICAL': 'darkred'
                                }.get(summary['urgency_level'], 'gray')
                                st.markdown(f"**Urgency:** <span style='color:{urgency_color}'>{summary['urgency_level']}</span>", unsafe_allow_html=True)
                        
                        # Tables
                        if extract_tables and result.get('tables'):
                            st.subheader("📋 Extracted Tables")
                            for i, table in enumerate(result['tables']):
                                st.write(f"**Table {i+1}:**")
                                if len(table) > 0 and len(table[0]) > 0:
                                    df = pd.DataFrame(table[1:], columns=table[0] if table[0] else [f"Col_{j}" for j in range(len(table[1]))])
                                    st.dataframe(df, use_container_width=True)
                    
                    except Exception as e:
                        st.error(f"❌ Processing failed: {str(e)}")
    
    with col2:
        st.subheader("💡 Tips")
        st.info("""
        **Supported formats:**
        - PDF documents
        - Word documents (.docx)
        - Images (PNG, JPG, TIFF)
        
        **Best results:**
        - Clear, high-resolution images
        - Text-based PDFs
        - Indonesian business documents
        """)
        
        if st.session_state.processed_docs:
            st.subheader("📁 Recent Documents")
            for doc in st.session_state.processed_docs[-3:]:
                st.write(f"📄 {doc['filename']}")
                st.caption(f"Processed: {doc['processed_at'][:19]}")

with tab2:
    st.header("🔍 Search Documents")
    
    if not st.session_state.processed_docs:
        st.info("No documents processed yet. Upload and process documents in the first tab.")
    else:
        search_query = st.text_input("Search documents", placeholder="Enter search terms...")
        
        if search_query:
            # Simple search through processed documents
            results = []
            for doc in st.session_state.processed_docs:
                content = doc['result'].get('content', '')
                if search_query.lower() in content.lower():
                    results.append(doc)
            
            st.write(f"Found {len(results)} documents matching '{search_query}'")
            
            for doc in results:
                with st.expander(f"📄 {doc['filename']}"):
                    st.write(f"**Processed:** {doc['processed_at'][:19]}")
                    
                    # Show relevant excerpt
                    content = doc['result'].get('content', '')
                    if search_query.lower() in content.lower():
                        start = content.lower().find(search_query.lower())
                        excerpt_start = max(0, start - 100)
                        excerpt_end = min(len(content), start + 200)
                        excerpt = content[excerpt_start:excerpt_end]
                        
                        # Highlight search term
                        highlighted = excerpt.replace(
                            search_query, 
                            f"**{search_query}**"
                        )
                        st.write(f"...{highlighted}...")
                    
                    if st.button(f"View full document", key=f"view_{doc['filename']}"):
                        st.json(doc['result'])

with tab3:
    st.header("📊 Analytics Dashboard")
    
    if not st.session_state.processed_docs:
        st.info("No data available. Process some documents first.")
    else:
        # Document types
        doc_types = [doc['result'].get('classification', {}).get('category', 'Unknown') for doc in st.session_state.processed_docs]
        type_counts = pd.Series(doc_types).value_counts()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Document Types")
            fig = px.pie(values=type_counts.values, names=type_counts.index, title="Distribution of Document Types")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Processing Times")
            times = [doc['processing_time'] for doc in st.session_state.processed_docs]
            fig = px.histogram(x=times, title="Processing Time Distribution", nbins=10)
            fig.update_xaxis(title="Processing Time (seconds)")
            fig.update_yaxis(title="Count")
            st.plotly_chart(fig, use_container_width=True)
        
        # Processing timeline
        st.subheader("Processing Timeline")
        timeline_data = []
        for doc in st.session_state.processed_docs:
            timeline_data.append({
                'filename': doc['filename'],
                'processed_at': doc['processed_at'],
                'processing_time': doc['processing_time'],
                'type': doc['result'].get('classification', {}).get('category', 'Unknown')
            })
        
        if timeline_data:
            df = pd.DataFrame(timeline_data)
            df['processed_at'] = pd.to_datetime(df['processed_at'])
            
            fig = px.scatter(df, x='processed_at', y='processing_time', 
                           color='type', hover_data=['filename'],
                           title="Document Processing Timeline")
            st.plotly_chart(fig, use_container_width=True)
        
        # Statistics table
        st.subheader("Detailed Statistics")
        stats_data = []
        for doc in st.session_state.processed_docs:
            result = doc['result']
            stats_data.append({
                'Filename': doc['filename'],
                'Type': result.get('classification', {}).get('category', 'Unknown'),
                'Confidence': f"{result.get('classification', {}).get('confidence', 0):.1%}",
                'Processing Time': f"{doc['processing_time']:.1f}s",
                'Entities Found': len(result.get('entities', {}).get('people', [])) + len(result.get('entities', {}).get('organizations', [])),
                'Tables Found': len(result.get('tables', [])),
            })
        
        st.dataframe(pd.DataFrame(stats_data), use_container_width=True)

with tab4:
    st.header("ℹ️ About AI Document Processor")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🚀 Features")
        st.markdown("""
        - **Multi-format Support**: PDF, DOCX, Images
        - **AI-Powered Extraction**: GPT-4 integration
        - **Indonesian Optimization**: Local language & context
        - **Entity Recognition**: People, organizations, dates, amounts
        - **Document Classification**: Automatic categorization
        - **Table Extraction**: Structured data recognition
        - **Smart Summarization**: Key insights generation
        """)
        
        st.subheader("🎯 Use Cases")
        st.markdown("""
        - **Banking**: KYC document processing
        - **Legal**: Contract analysis & review
        - **Government**: Permit & application processing
        - **Healthcare**: Medical record digitization
        - **Manufacturing**: Invoice & certificate processing
        """)
    
    with col2:
        st.subheader("🏢 Business Impact")
        
        # ROI Calculator
        st.write("**ROI Calculator**")
        docs_per_month = st.number_input("Documents processed per month", value=1000, min_value=1)
        manual_time = st.number_input("Manual processing time per doc (minutes)", value=30, min_value=1)
        hourly_rate = st.number_input("Staff hourly rate (IDR)", value=50000, min_value=1000)
        
        # Calculate savings
        monthly_manual_hours = (docs_per_month * manual_time) / 60
        monthly_manual_cost = monthly_manual_hours * hourly_rate
        
        # AI processing (assume 1 minute per doc)
        monthly_ai_hours = docs_per_month / 60
        monthly_ai_cost = monthly_ai_hours * hourly_rate
        ai_service_cost = docs_per_month * 5000  # Rp 5,000 per document
        
        monthly_savings = monthly_manual_cost - (monthly_ai_cost + ai_service_cost)
        annual_savings = monthly_savings * 12
        
        st.success(f"""
        **Monthly Savings**: Rp {monthly_savings:,.0f}
        **Annual Savings**: Rp {annual_savings:,.0f}
        **ROI**: {(annual_savings / (ai_service_cost * 12)) * 100:.0f}%
        """)
        
        st.subheader("📞 Contact")
        st.markdown("""
        **Enterprise Solutions Available**
        - Custom integrations
        - On-premise deployment
        - Advanced analytics
        - 24/7 support
        
        📧 enterprise@yourdomain.com
        📱 +62-xxx-xxxx-xxxx
        """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>🤖 AI Document Processor v1.0 | Built for Indonesian Businesses | 
    <a href='https://github.com/yourusername/ai-doc-indo' target='_blank'>GitHub</a></p>
</div>
""", unsafe_allow_html=True)

# Clear data button (in sidebar)
with st.sidebar:
    st.markdown("---")
    if st.button("🗑️ Clear All Data", type="secondary"):
        st.session_state.processed_docs = []
        st.experimental_rerun()
