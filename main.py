from llama_index.llms.groq import Groq
from llama_index.core import SimpleDirectoryReader, ServiceContext, VectorStoreIndex
from llama_index.core import Document
from llama_index.llms.groq import Groq

import streamlit as st
from pathlib import Path
import os
import time
from streamlit_js_eval import streamlit_js_eval


GROQ_API_KEY = "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"

def create_index(file_name=None):
    documents = SimpleDirectoryReader(
        input_files=[file_name]).load_data()



    document = Document(text="\n\n".join([doc.text for doc in documents]))

    llm = Groq(model="mixtral-8x7b-32768", api_key=GROQ_API_KEY )


    llm_2 = Groq(model="llama3-70b-8192", api_key=GROQ_API_KEY )

    service_context = ServiceContext.from_defaults(
        llm=llm_2, embed_model="local:BAAI/bge-small-en-v1.5")


    service_context = ServiceContext.from_defaults(
        llm=llm_2, embed_model="local:BAAI/bge-small-en-v1.5"
    )
    index = VectorStoreIndex.from_documents([document],
                                            service_context=service_context)
    return "ready", index

def chat(prompt=None, index=None):
    query_engine = index.as_query_engine()

    response = query_engine.query(
       prompt
    )
    print(str(response))
    return str(response)

def file_upload_and_index():
        
    save_folder = "upload"
    with st.sidebar:
        file = st.file_uploader(label="Upload your file:")
        if file:
        
            save_path = Path(save_folder, file.name)
            with open(save_path, mode='wb') as w:
                w.write(file.getvalue())
            
            
            for f in os.listdir("upload"):
                if f.endswith(".pdf"):
                    file_path = os.path.join(save_folder, f)
                    with st.spinner('Creating a knowledge-base, Please wait'):
                        stat, index = create_index(file_path)
            return stat, index
        
        
            



st.header('Chat with your pdf', divider='rainbow')
st.caption('_Upload your document and chat with it in realtime!_')





if 'stat' not in st.session_state:
    try:
        stat, index = file_upload_and_index()
        st.session_state['stat'] = stat
        st.session_state['index'] = index
    except:
        st.write("Please upload a file")






if 'stat' in st.session_state:
    prompt = st.chat_input("Say something")
    if prompt:
        with st.chat_message("user"):
            st.write(prompt)

        
        
        with st.spinner("Thinking..."):
            resp = chat(prompt=prompt, index=st.session_state['index'])
            with st.sidebar:
                if st.button("Start a new chat"):
                    streamlit_js_eval(js_expressions="parent.window.location.reload()")
                    keys = list(st.session_state.keys())
                    for key in keys:
                        st.session_state.pop(key)

                    
                    

            def stream_data():
                for word in resp.split(" "):
                    yield word + " "
                    time.sleep(0.02)
            print("Ok")
                    
            with st.chat_message("assistant"):
                st.write_stream(stream_data)
        
