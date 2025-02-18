import os
from io import BytesIO

try:
    import pandas as pd
except ModuleNotFoundError:
    os.system('pip install pandas')

try:
    import streamlit as st
except ModuleNotFoundError:
    os.system('pip install streamlit')
    
os.system('cls') #clear terminal screen

# Setup Streamlit App
st.set_page_config(page_title='🤖 Data Sweeper', layout='wide')
st.title('🤖 Data Sweeper')
st.write('📁 Transform your files between CSV and Excel format with built-in data cleaning and visualization')

# File uploader
all_files = st.file_uploader(
    'Upload your Files (Only CSV and Excel files)',
    type=['xlsx', 'csv'],
    accept_multiple_files=True
)

if all_files:
    for file in all_files:
        st.session_state.file_name = file.name
        file_extension = os.path.splitext(st.session_state.file_name)[-1].lower()
        
        if file_extension == '.csv':
            st.session_state.df = pd.read_csv(file)
        elif file_extension == '.xlsx':
            st.session_state.df = pd.read_excel(file)
        else:
            st.error(f'{file_extension}, Unsupported file. Please upload CSV or Excel file')
            continue
        
        st.write(f"**File Format :** {file_extension}")
        st.write(f'**File Size :** {file.size/1024:.2f} KB')
        
        st.subheader('Preview the Data Frame')
        st.dataframe(st.session_state.df)
        
        st.subheader("Data Cleaning Options")
        if st.checkbox(f'Clean data for {st.session_state.file_name}'):
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button(f'Remove {st.session_state.df.duplicated().sum()} Duplicates', icon='📁'):
                    st.session_state.df = st.session_state.df.drop_duplicates().reset_index(drop=True)
                    st.session_state.cleaned_df = st.session_state.df.copy()  # Store cleaned data
                    st.write("✅ Duplicates removed!")
                    st.dataframe(st.session_state.df)
            
            with col2:
                if st.button(f'Fill Missing Values', icon='🫙'):
                    numeric_cols = st.session_state.df.select_dtypes(include=['number']).columns
                    st.session_state.df[numeric_cols] = st.session_state.df[numeric_cols].fillna(st.session_state.df[numeric_cols].mean())
                    st.write("✅ Missing values filled!")
        
        st.subheader('Select Columns to Keep')
        selected_columns = st.multiselect("Choose Columns", st.session_state.df.columns, default=st.session_state.df.columns)
        st.session_state.df = st.session_state.df[selected_columns]
        
        st.subheader('Conversion Options')
        conversion_option = st.radio("Convert to:", options=['CSV', 'Excel'], key=st.session_state.file_name)
        
        if st.button(f'Convert & Download as {conversion_option}'):
            buffer = BytesIO()
            
            if 'cleaned_df' in st.session_state:
                df_to_save = st.session_state.cleaned_df  # Ensure cleaned data is used
            else:
                df_to_save = st.session_state.df
            
            if conversion_option == 'CSV':
                df_to_save.to_csv(buffer, index=False)
                file_save_as = st.session_state.file_name.replace(file_extension, '.csv')
                mime_type = 'text/csv'
            else:
                df_to_save.to_excel(buffer, index=False)
                file_save_as = st.session_state.file_name.replace(file_extension, '.xlsx')
                mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            
            buffer.seek(0)
            
            st.download_button(
                label=f'⬇️ Download {st.session_state.file_name} as {conversion_option}',
                file_name=file_save_as,
                data=buffer,
                mime=mime_type
            )
