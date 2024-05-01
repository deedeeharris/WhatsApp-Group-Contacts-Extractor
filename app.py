import streamlit as st
import pandas as pd
import re

def process_chat(file_path):
    join_pattern = r'\d+\.\d+\.\d+, \d+:\d+ - \u200fההצטרפות של (.*?) בוצעה'
    leave_pattern = r'\d+\.\d+\.\d+, \d+:\d+ - (.*?) יצא/ה'

    join_data = []
    leave_data = []

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            join_match = re.search(join_pattern, line)
            leave_match = re.search(leave_pattern, line)
            if join_match:
                datetime, user_info = line.split(' - ')[:2]
                user = join_match.group(1)
                join_data.append((datetime, user))
            if leave_match:
                datetime, user_info = line.split(' - ')[:2]
                user = leave_match.group(1)
                leave_data.append((datetime, user))

    df_joins = pd.DataFrame(join_data, columns=['Datetime', 'User'])
    df_leaves = pd.DataFrame(leave_data, columns=['Datetime', 'User'])

    df_joins['Action'] = 'Joined'
    df_leaves['Action'] = 'Left'
    df_combined = pd.concat([df_joins, df_leaves])
    df_combined['Datetime'] = pd.to_datetime(df_combined['Datetime'], format='%d.%m.%Y, %H:%M')
    df_combined.sort_values(by='Datetime', inplace=True)

    final_status = df_combined.groupby('User').last()['Action'].reset_index()
    final_status['Status'] = final_status['Action'].map({'Joined': 'In', 'Left': 'Out'})
    final_status = final_status[['User', 'Status']]
    
    return final_status

def save_df_to_excel(df):
    output_path = 'WhatsApp_Group_Status.xlsx'
    df.to_excel(output_path, index=False)
    return output_path

st.title('WhatsApp Group Status Processor')

uploaded_file = st.file_uploader("Choose a WhatsApp chat log file (.txt)")
if uploaded_file is not None:
    with open("temp_chat_file.txt", "wb") as f:
        f.write(uploaded_file.getvalue())
    processed_data = process_chat("temp_chat_file.txt")
    output_file = save_df_to_excel(processed_data)
    st.download_button(
        label="Download Excel file with Status",
        data=open(output_file, "rb"),
        file_name=output_file,
        mime="application/vnd.ms-excel"
    )
