import streamlit as st
import pandas as pd
from datetime import datetime
import numpy as np

st.set_page_config(page_title="IVT Averager", page_icon=None, layout="wide", initial_sidebar_state=None, menu_items=None)
st.title("IVT Data Averager")


st.info("This automatically drops unused columns such as Date, Area, User, etc. It also formats it to only show the averaged rows.")
uploaded_file = st.file_uploader(label = "Upload file here", type=["csv", "xlsx", "xls"], accept_multiple_files=False)

def remove_outliers(group, threshold=1.5):
    # Select only numeric columns to check for outliers
    numeric_cols = group.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        numeric_cols = group.select_dtypes(include=[np.number]).columns
        indices_to_drop = set()

        for col in numeric_cols:
            mean = group[col].mean()
            sd = group[col].std()
            
            if sd > 0:
                outlier_indices = group[np.abs(group[col] - mean) > (threshold * sd)].index
                indices_to_drop.update(outlier_indices)
        
        if indices_to_drop:
            return group.drop(index=indices_to_drop)
        
    return group

if uploaded_file:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file) 
           
    cols_to_drop = ["Date", "Area(cm2)", "User", "Grading", "Device ID", "IR(A)" ]
    df = df.drop(columns=cols_to_drop, errors='ignore')

    group_id = (df["ID"] != df["ID"].shift()).cumsum()

    # We group by the ID sequence and apply our outlier filter
    cleaned_df = df.groupby(group_id, group_keys=False).apply(remove_outliers)

    avg_df = df.groupby(group_id).agg({
            "ID": 'first', 
            **{col: 'mean' for col in df.select_dtypes('number').columns} 
        }).round(4)
    avg_df = avg_df.rename(columns={"ID": 'Sample ID'})
    avg_df = avg_df.sort_values(by="Sample ID")

    st.subheader("Averages")
    st.dataframe(avg_df, width="stretch")

    with st.expander("View Raw Data"):
        report_list = []
        numeric_cols = cleaned_df.select_dtypes('number').columns

        for _, group in cleaned_df.groupby(group_id):
            report_list.append(group)
            
            avg_row = group[numeric_cols].mean().to_frame().T
            avg_row["ID"] = f"AVERAGE: {group['ID'].iloc[0]}"
            avg_row = avg_row.round(4)
            report_list.append(avg_row)
            
            spacer = pd.DataFrame([[""] * len(cleaned_df.columns)], columns=cleaned_df.columns)
            report_list.append(spacer)

        interleaved_df = pd.concat(report_list, ignore_index=True)
        st.dataframe(interleaved_df, use_container_width=True)
    
    today = datetime.today()
    csv = avg_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Averages",
        data=csv,
        file_name=f"{today.strftime("%M%D%Y")}_averaged_IVT.excel",
        mime="text/csv",)

else:
    st.info("Upload excel file first.")
