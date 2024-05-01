import streamlit as st
import pandas as pd
import re

def process_chat((file_path):
    # Adjusted regex patterns for enhanced extraction
    join_patterns = [
        r'\d+/\d+/\d+, \d+:\d+ - (.+?) joined using this community\'s invite link',  # English joins
        r'\d+\.\d+\.\d+, \d+:\d+ - \u200fההצטרפות של (.*?) בוצעה'  # Hebrew joins
    ]
    leave_patterns = [
        r'\d+/\d+/\d+, \d+:\d+ - (.+?) left',  # English leaves
        r'\d+\.\d+\.\d+, \d+:\d+ - (.*?) יצא/ה',  # Hebrew leaves
        r'\d+/\d+/\d+, \d+:\d+ - (.+?), and \d+ others left'  # English multiple leaves
    ]

    join_data = []
    leave_data = []
    
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in lines:
            for pattern in join_patterns:
                join_match = re.search(pattern, line)
                if join_match:
                    datetime, user_info = line.split(' - ')[:2]
                    user = join_match.group(1)
                    join_data.append((datetime, user))
    
            for pattern in leave_patterns:
                leave_match = re.search(pattern, line)
                if leave_match:
                    datetime, user_info = line.split(' - ')[:2]
                    user = leave_match.group(1)
                    leave_data.append((datetime, user))

    # Create dataframes and process the data to determine final status
    df_joins = pd.DataFrame(join_data, columns=['Datetime', 'User'])
    df_leaves = pd.DataFrame(leave_data, columns=['Datetime', 'User'])
    df_joins['Action'] = 'Joined'
    df_leaves['Action'] = 'Left'
    df_combined = pd.concat([df_joins, df_leaves])
    df_combined['Datetime'] = pd.to_datetime(df_combined['Datetime'], errors='coerce')
    df_combined.sort_values(by='Datetime', inplace=True)

    final_status = df_combined.groupby('User').last()['Action'].reset_index()
    final_status['Status'] = final_status['Action'].map({'Joined': 'In', 'Left': 'Out'})
    final_status = final_status[['User', 'Status']]
    
    # Remove duplicates based on 'User' and keep the last occurrence
    final_status.drop_duplicates(subset='User', keep='last', inplace=True)
    
    # Sort final_status by 'Status' column so 'In' comes before 'Out'
    final_status.sort_values(by='Status', ascending=True, inplace=True)
    
    return final_status

def save_df_to_excel(df):
    output_path = 'WhatsApp_Group_Status.xlsx'
    df.to_excel(output_path, index=False)
    return output_path

st.markdown('''# WhatsApp Group Contacts Extractor

## Instructions:

1. **Export WhatsApp Chat History**:
   - Open the WhatsApp group that you manage.
   - Navigate to the group's settings or options.
   - Look for the "Export Chat" or "Export Chat History" feature.
   - Choose to export the chat without media (text-only format).
   - Save the exported chat file to your device.

2. **Upload the Chat History**:
   - Open this app.
   - Click on the file uploader component labeled "Choose a WhatsApp chat log file (.txt)".
   - Select the exported chat text file from your device for upload.

3. **Process and Download**:
   - Once the chat file is uploaded, the app will process it to extract user join and leave events.
   - After processing, download the excel file.

4. **Language Support**:
   - The app assumes that the WhatsApp chat log is in Hebrew.
   - For support in other languages, please contact Yedidya Harris.

5. **Disclaimer**:
   - Use the app at your own risk.
   - This app was developed by Yedidya Harris. For inquiries or feedback, you can contact Yedidya Harris via [LinkedIn](https://www.linkedin.com/in/yedidya-harris/).

''')
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
