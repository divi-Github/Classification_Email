import streamlit as st
import requests
import base64
import io

API_URL = "https://140ce3b927c1.ngrok-free.app/process/split-container-pdf"

st.set_page_config(
    page_title="PDF Container Splitter & Viewer",
    layout="wide"
)

st.title("PDF Container Splitter & Viewer 📄✂️")
st.markdown("Upload a PDF file, then click **Process PDF** to send it to the **Container Splitter API**. You can now **preview** and **download** the split containers.")


uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

st.markdown("""
<style>
/* Style for the HTML download link to look like a standard Streamlit button */
.download-button-link {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-weight: 500;
    padding: 0.25rem 0.75rem;
    border-radius: 0.25rem;
    margin: 0.5rem 0 0.5rem 0; 
    line-height: 1.6;
    color: white !important;
    background-color: rgb(14, 17, 23); 
    text-decoration: none; 
    border: 1px solid rgb(14, 17, 23);
    cursor: pointer;
    transition: background-color 0.3s;
}

.download-button-link:hover {
    background-color: rgb(40, 40, 40); 
    color: white !important;
    text-decoration: none; 
}

.pdf-viewer-iframe {
    width: 100%;
    height: 600px; /* Set a fixed height for a good viewing area */
    border: 1px solid #ccc;
    border-radius: 4px;
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)


#  Process Button 
if uploaded_file is not None:
    st.info(f"File **'{uploaded_file.name}'** uploaded and ready for processing.")
    
    process_button = st.button("Process PDF", key="process_api")

    if process_button:
        #  API Processing
        st.info(f"Sending file to API at **{API_URL}**...")

        
        files = {
            'file': (uploaded_file.name, uploaded_file.getvalue(), 'application/pdf')
        }

        # API 
        try:
          
            with st.spinner('Processing PDF... this might take a moment.', show_time=True):

                response = requests.post(
                    API_URL, 
                    files=files, 
                    headers={'accept': 'application/json'},
                    timeout=300 
                )
            
          
            if response.status_code == 200:
                data = response.json()
                
                st.success("API call successful! Use the sections below to **preview** and **download** the split containers.")

               
                with st.expander("View Raw JSON Response"):
                    st.json(data)
                    
                #  Results Processing 
                if "splits" in data and isinstance(data["splits"], list):
                    
                    st.header(f"Results: {data.get('containers_detected', 'N/A')} Containers Detected")
                    
                    for i, split in enumerate(data["splits"]):
                        container_id = split.get("container", f"Split {i+1}")
                        page_range = split.get("page_range", "N/A")
                        base64_pdf_string = split.get("base64") 
                        
                        st.subheader(f"📦 Container: **{container_id}** (Pages: {page_range})")
                        
                        if base64_pdf_string:
                            try:
                                file_name = f"{container_id}_{page_range.replace(' ', '_')}.pdf"
                                data_url = f"data:application/pdf;base64,{base64_pdf_string}"
                                
                                #  1. DOWNLOAD LINK
                                download_link_html = f"""
                                    <a href="{data_url}" 
                                        download="{file_name}"
                                        class="download-button-link">
                                        📥 Download {file_name}
                                    </a>
                                """
                                st.markdown(download_link_html, unsafe_allow_html=True)
                                
                                #  2. PDF PREVIEW 
                                preview_html = f"""
                                <iframe class="pdf-viewer-iframe" 
                                    src="{data_url}" 
                                    title="PDF Preview for {container_id}">
                                </iframe>
                                """
                                st.markdown(preview_html, unsafe_allow_html=True)
                                
                                st.markdown("---")
                                
                            except Exception as e:
                                st.error(f"Error creating download/preview for {container_id}: {e}")
                        else:
                            st.warning(f"No Base64 PDF data found for {container_id}.")

                else:
                    st.error("API response structure is unexpected. Please check the format of the returned data.")
                    with st.expander("View Raw JSON Response (for debugging)"):
                        st.json(data)

            elif response.status_code == 404:
                st.error(f"Error: API endpoint not found (Status **{response.status_code}**). Please verify the URL: **{API_URL}**")
            else:
                st.error(f"API call failed with status code: **{response.status_code}**")
                try:
                    st.json(response.json())
                except requests.exceptions.JSONDecodeError:
                    st.code(response.text)
                
        except requests.exceptions.Timeout:
            st.error(f"API request timed out after **300 seconds** (5 minutes). Please check your API's performance or increase the timeout.")
        except requests.exceptions.RequestException as e:
            st.error(f"An error occurred during the API request. Error: **{e}**")
