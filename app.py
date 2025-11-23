import streamlit as st
from langchain_community.document_loaders import WebBaseLoader
from chains import Chain
from portfolio import Portfolio
from utils import clean_text
import os

def create_streamlit_app(llm, portfolio, clean_text):
    st.set_page_config(
        page_title="Cold Email Generator",
        page_icon="📧",
        layout="wide"
    )
    
    # Custom CSS
    st.markdown("""
        <style>
        .main {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .stButton>button {
            background-color: #667eea;
            color: white;
            font-weight: bold;
            border-radius: 10px;
            padding: 10px 24px;
            border: none;
        }
        .stButton>button:hover {
            background-color: #5568d3;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Header
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("📧 Cold Email Generator")
        st.markdown("### Generate personalized cold emails for job postings using AI")
    
    # API Key input
    api_key = st.text_input(
        "Enter your Groq API Key",
        type="password",
        help="Get your free API key from https://console.groq.com/keys"
    )
    
    if api_key:
        os.environ["GROQ_API_KEY"] = api_key
    
    # URL input
    url_input = st.text_input(
        "Enter Company Career Page URL:",
        placeholder="https://company.com/careers",
        help="Enter the URL of the company's careers or job posting page"
    )
    
    submit_button = st.button("🚀 Generate Cold Emails")
    
    if submit_button:
        if not api_key:
            st.error("⚠️ Please enter your Groq API key to continue")
            return
        
        if not url_input:
            st.error("⚠️ Please enter a valid URL")
            return
        
        try:
            with st.spinner("🔍 Extracting job information..."):
                # Load and clean webpage content
                loader = WebBaseLoader([url_input])
                data = clean_text(loader.load().pop().page_content)
                
                # Load portfolio
                portfolio.load_portfolio()
                
                # Extract jobs using LLM
                jobs = llm.extract_jobs(data)
                
                if not jobs:
                    st.warning("No job postings found on this page. Please try a different URL.")
                    return
                
                st.success(f"✅ Found {len(jobs)} job posting(s)!")
            
            # Display jobs and generated emails
            for idx, job in enumerate(jobs):
                with st.container():
                    st.markdown("---")
                    
                    # Job details
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"### 💼 {job.get('role', 'N/A')}")
                        st.markdown(f"**Experience Required:** {job.get('experience', 'N/A')}")
                        
                        # Skills
                        if job.get('skills'):
                            st.markdown("**Required Skills:**")
                            skills_html = " ".join([
                                f'<span style="background-color: #667eea; color: white; padding: 5px 10px; '
                                f'border-radius: 15px; margin: 2px; display: inline-block; font-size: 14px;">{skill}</span>'
                                for skill in job['skills']
                            ])
                            st.markdown(skills_html, unsafe_allow_html=True)
                        
                        # Description
                        st.markdown(f"**Description:**")
                        st.write(job.get('description', 'N/A'))
                    
                    with col2:
                        st.info(f"📊 Job #{idx + 1}")
                    
                    # Query portfolio for matching projects
                    skills = job.get('skills', [])
                    links = portfolio.query_links(skills)
                    
                    # Generate email
                    with st.spinner("✍️ Generating personalized email..."):
                        email = llm.write_mail(job, links)
                    
                    # Display email
                    st.markdown("### 📧 Generated Cold Email")
                    st.code(email, language=None)
                    
                    # Copy button
                    st.download_button(
                        label="📋 Download Email",
                        data=email,
                        file_name=f"cold_email_{job.get('role', 'job').replace(' ', '_')}.txt",
                        mime="text/plain",
                        key=f"download_{idx}"
                    )
                    
                    # Show matched portfolio links
                    if links:
                        with st.expander("🔗 Matched Portfolio Projects"):
                            for link in links:
                                st.markdown(f"- {link}")
        
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
            st.info("💡 Tip: Make sure the URL is accessible and contains job posting information.")

if __name__ == "__main__":
    chain = Chain()
    portfolio = Portfolio()
    create_streamlit_app(chain, portfolio, clean_text)