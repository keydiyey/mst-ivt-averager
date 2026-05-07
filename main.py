import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="IVT Averager", page_icon=None, layout="wide", initial_sidebar_state=None, menu_items=None)
st.title("IVT Data Averager")


st.info("This automatically drops unused columns such as Date, Area, User, etc. It also formats it to only show the averaged rows.")
uploaded_file = st.file_uploader(label = "Upload file here", type=["csv", "xlsx", "xls"], accept_multiple_files=False)

if uploaded_file:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file) 
           
    cols_to_drop = ["Date", "Area(cm2)", "User", "Grading", "Device ID", "IR(A)" ]
    df = df.drop(columns=cols_to_drop, errors='ignore')

    group_id = (df["ID"] != df["ID"].shift()).cumsum()

    avg_df = df.groupby(group_id).agg({
            "ID": 'first', 
            **{col: 'mean' for col in df.select_dtypes('number').columns} 
        }).round(4)
    avg_df = avg_df.rename(columns={"ID": 'Sample ID'})
    avg_df = avg_df.sort_values(by="Sample ID")

    st.subheader("Averages")
    st.info("You can copy the cells directly to the spreadsheet but you can also download the csv file.")
    st.dataframe(avg_df, width="stretch")
    

    
    today = datetime.today()
    csv = avg_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Averages",
        data=csv,
        file_name=f"{today.strftime("%M%D%Y")}_averaged_IVT.excel",
        mime="text/csv",
)

else:
    st.info("Upload excel file first.")
