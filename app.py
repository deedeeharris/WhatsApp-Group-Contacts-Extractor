import streamlit as st
import re
import pandas as pd

def process_whatsapp_chat_log(file_obj, output_excel_path):
    # Define regex patterns for detecting joins and leaves
    join_pattern = r'\d+\.\d+\.\d+, \d+:\d+ - \u200fההצטרפות של (.+?) בוצעה'
    leave_pattern = r'\d+\.\d+\.\d+, \d+:\d+ - (.+?) יצא/ה'

    # Lists to store join and leave data
    join_data = []
    leave_data = []

    # Read the file contents and extract events
    lines = file_obj.readlines()
    for line in lines:
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

    # Create DataFrames for joins and leaves
    df_joins = pd.DataFrame(join_data, columns=['Datetime', 'User'])
    df_leaves = pd.DataFrame(leave_data, columns=['Datetime', 'User'])

    # Tag actions in each DataFrame
    df_joins['Action'] = 'Joined'
    df_leaves['Action'] = 'Left'

    # Combine the DataFrames and sort by datetime
    df_combined = pd.concat([df_joins, df_leaves])
    df_combined['Datetime'] = pd.to_datetime(df_combined['Datetime'], format='%d.%m.%Y, %H:%M')
    df_combined.sort_values(by='Datetime', inplace=True)

    # Get the last action of each user to determine final status
    final_status = df_combined.groupby('User').last()['Action'].reset_index()
    final_status['Status'] = final_status['Action'].map({'Joined': 'In', 'Left': 'Out'})
    final_status = final_status[['User', 'Status']]

    # Sort final_status by 'Status' column so 'In' comes before 'Out'
    final_status.sort_values(by='Status', ascending=True, inplace=True)

    # Save the results to an Excel file
    final_status.to_excel(output_excel_path, index=False)
    st.success(f"The final status has been saved to {output_excel_path}")

def main():
    st.title("WhatsApp Chat Log Processor")

    st.write("This app processes WhatsApp chat logs in Hebrew and generates an Excel file.")

    uploaded_file = st.file_uploader("Upload your WhatsApp chat log file", type=['txt'])

    if uploaded_file is not None:
        output_excel_path = "processed_chat_log.xlsx"

        process_whatsapp_chat_log(uploaded_file, output_excel_path)

        st.download_button(
            label="Download Processed Excel File",
            data=output_excel_path,
            file_name="processed_chat_log.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

if __name__ == "__main__":
    main()

