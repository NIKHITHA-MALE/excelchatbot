import pandas as pd
import streamlit as st
import re
import os
from datetime import datetime

# ========== STEP 1: FILE PATHS AND DATA LOADING ==========
# Define file paths
ORIGINAL_DATA_FILE = r'C:\Users\DELL\OneDrive\Desktop\newmsme\Employe_Performance_dataset.csv'
NEW_DATA_FILE = r'C:\Users\DELL\OneDrive\Desktop\newmsme\new_employees.csv'
MASTER_DATA_FILE = r'C:\Users\DELL\OneDrive\Desktop\newmsme\combined_employees.csv'

# Load data with caching - UPDATED VERSION
@st.cache_data
def load_data():
    """
    Load and combine data, handling deletions and duplicates
    """
    # Load original data
    df_original = pd.read_csv(ORIGINAL_DATA_FILE)
    
    # Initialize with original data
    df_combined = df_original.copy()
    
    # Check if new employees file exists and has data
    if os.path.exists(NEW_DATA_FILE):
        df_new = pd.read_csv(NEW_DATA_FILE)
        
        # Filter out any completely empty rows
        df_new = df_new.dropna(how='all')
        
        if not df_new.empty:
            # Check for valid data (rows with at least a name or ID)
            df_new = df_new.dropna(subset=['Name', 'ID'], how='all')
            
            if not df_new.empty:
                # Remove any potential duplicates by ID
                # Keep only the most recent entry for each ID
                df_new = df_new.sort_values('ID').drop_duplicates(subset='ID', keep='last')
                
                # First, remove any IDs from df_combined that are in df_new (update/replace)
                df_combined = df_combined[~df_combined['ID'].isin(df_new['ID'])]
                
                # Then append the new data
                df_combined = pd.concat([df_combined, df_new], ignore_index=True)
    
    # Sort by ID for consistency
    df_combined = df_combined.sort_values('ID').reset_index(drop=True)
    
    return df_combined

def save_combined_data():
    """Save the combined data to a master file"""
    df_combined = load_data()  # This loads the combined data
    df_combined.to_csv(MASTER_DATA_FILE, index=False)
    return df_combined

def refresh_data():
    """
    Completely refresh and clean the data
    """
    # Clear cache first
    st.cache_data.clear()
    
    # Load fresh data
    df = load_data()
    
    # Optional: Save a clean copy
    df.to_csv('cleaned_employee_data.csv', index=False)
    
    return df

# ========== STEP 2: ADD NEW EMPLOYEE FUNCTION ==========
def add_new_employee(df, employee_data):
    """
    Add a new employee to the dataset
    
    Args:
        df: Current dataframe
        employee_data: Dictionary containing employee details
    
    Returns:
        Updated dataframe
    """
    # Generate new ID (max existing ID + 1)
    new_id = df['ID'].max() + 1 if len(df) > 0 else 1
    
    # Create new employee record
    new_employee = {
        'ID': new_id,
        'Name': employee_data.get('name', '').strip(),
        'Age': employee_data.get('age', ''),
        'Gender': employee_data.get('gender', ''),
        'Department': employee_data.get('department', ''),
        'Salary': employee_data.get('salary', ''),
        'Joining Date': employee_data.get('joining_date', datetime.now().strftime('%d-%m-%Y')),
        'Performance Score': employee_data.get('performance_score', ''),
        'Experience': employee_data.get('experience', ''),
        'Status': employee_data.get('status', 'Active'),
        'Location': employee_data.get('location', ''),
        'Session': employee_data.get('session', 'Morning')
    }
    
    # Append to new employees CSV
    new_df = pd.DataFrame([new_employee])
    
    if os.path.exists(NEW_DATA_FILE):
        existing_new = pd.read_csv(NEW_DATA_FILE)
        # Filter out empty rows before appending
        existing_new = existing_new.dropna(how='all')
        updated_new = pd.concat([existing_new, new_df], ignore_index=True)
    else:
        updated_new = new_df
    
    updated_new.to_csv(NEW_DATA_FILE, index=False)
    
    # Clear cache to reload fresh data
    st.cache_data.clear()
    
    return new_employee

# ========== STEP 3: MODIFIED PROCESS_QUESTION FUNCTION ==========
def process_question(question, df):
    question = question.lower().strip()
    
    # Check if user wants to add an employee
    if any(phrase in question for phrase in ['add employee', 'new employee', 'hire employee']):
        return "To add a new employee, please go to the '➕ Add Employee' tab. Would you like me to take you there?"
    
    # ID-based queries
    if 'id' in question:
        # Extract ID number from question
        id_match = re.search(r'id\s*(\d+)', question)
        if not id_match:
            id_match = re.search(r'(\d+)', question)
        
        if id_match:
            employee_id = int(id_match.group(1))
            if employee_id in df['ID'].values:
                employee_data = df[df['ID'] == employee_id].iloc[0]
                
                if 'salary' in question:
                    return f"Salary of ID {employee_id} ({employee_data['Name']}): ${employee_data['Salary']}"
                elif 'name' in question:
                    return f"Name of ID {employee_id}: {employee_data['Name']}"
                elif 'age' in question:
                    return f"Age of ID {employee_id}: {employee_data['Age']} years"
                elif 'department' in question:
                    return f"Department of ID {employee_id}: {employee_data['Department']}"
                elif 'performance' in question:
                    perf_score = employee_data['Performance Score']
                    return f"Performance Score of ID {employee_id}: {perf_score if pd.notna(perf_score) else 'Not available'}"
                elif 'experience' in question:
                    return f"Experience of ID {employee_id}: {employee_data['Experience']} years"
                elif 'status' in question:
                    return f"Status of ID {employee_id}: {employee_data['Status']}"
                elif 'location' in question:
                    return f"Location of ID {employee_id}: {employee_data['Location']}"
                else:
                    # Return all information for the ID
                    info = f"Employee ID {employee_id} Details:\n"
                    info += f"Name: {employee_data['Name']}\n"
                    info += f"Age: {employee_data['Age']}\n"
                    info += f"Gender: {employee_data['Gender']}\n"
                    info += f"Department: {employee_data['Department']}\n"
                    info += f"Salary: ${employee_data['Salary']}\n"
                    info += f"Joining Date: {employee_data['Joining Date']}\n"
                    perf_score = employee_data['Performance Score']
                    info += f"Performance Score: {perf_score if pd.notna(perf_score) else 'Not available'}\n"
                    info += f"Experience: {employee_data['Experience']} years\n"
                    info += f"Status: {employee_data['Status']}\n"
                    info += f"Location: {employee_data['Location']}\n"
                    info += f"Session: {employee_data['Session']}"
                    return info
            else:
                return f"ID {employee_id} not found in the dataset."
    
    # Name-based queries
    elif any(word in question for word in ['who is', 'tell me about', 'information about']):
        name_match = re.search(r'(?:who is|tell me about|information about)\s+([a-zA-Z\s\.]+)', question)
        if name_match:
            name = name_match.group(1).strip()
            # Try to find the name in the dataset
            matches = df[df['Name'].str.contains(name, case=False, na=False)]
            if len(matches) > 0:
                if len(matches) == 1:
                    employee_data = matches.iloc[0]
                    info = f"Information about {employee_data['Name']}:\n"
                    info += f"ID: {employee_data['ID']}\n"
                    info += f"Age: {employee_data['Age']}\n"
                    info += f"Department: {employee_data['Department']}\n"
                    info += f"Salary: ${employee_data['Salary']}\n"
                    perf_score = employee_data['Performance Score']
                    info += f"Performance Score: {perf_score if pd.notna(perf_score) else 'Not available'}\n"
                    info += f"Status: {employee_data['Status']}"
                    return info
                else:
                    return f"Multiple employees found with name containing '{name}'. Please be more specific."
            else:
                return f"No employee found with name containing '{name}'."
    
    # Statistical queries
    elif 'average' in question:
        if 'salary' in question:
            avg_salary = df['Salary'].mean()
            return f"Average salary: ${avg_salary:.2f}"
        elif 'age' in question:
            avg_age = df['Age'].mean()
            return f"Average age: {avg_age:.1f} years"
        elif 'performance' in question:
            avg_perf = df['Performance Score'].mean()
            return f"Average performance score: {avg_perf:.2f}"
    
    # Department queries
    elif 'department' in question:
        if 'how many' in question or 'count' in question:
            if 'hr' in question or 'human resources' in question:
                count = len(df[df['Department'] == 'HR'])
                return f"Total employees in HR department: {count}"
            elif 'it' in question:
                count = len(df[df['Department'] == 'IT'])
                return f"Total employees in IT department: {count}"
            elif 'sales' in question:
                count = len(df[df['Department'] == 'Sales'])
                return f"Total employees in Sales department: {count}"
            else:
                dept_counts = df['Department'].value_counts()
                result = "Employees per department:\n"
                for dept, count in dept_counts.items():
                    result += f"{dept}: {count}\n"
                return result
    
    # Status queries
    elif 'active' in question or 'inactive' in question:
        if 'how many active' in question:
            active_count = len(df[df['Status'] == 'Active'])
            return f"Total active employees: {active_count}"
        elif 'how many inactive' in question:
            inactive_count = len(df[df['Status'] == 'Inactive'])
            return f"Total inactive employees: {inactive_count}"
    
    # Location queries
    elif 'location' in question:
        if 'how many in' in question:
            if 'new york' in question:
                count = len(df[df['Location'] == 'New York'])
                return f"Employees in New York: {count}"
            elif 'los angeles' in question:
                count = len(df[df['Location'] == 'Los Angeles'])
                return f"Employees in Los Angeles: {count}"
            elif 'chicago' in question:
                count = len(df[df['Location'] == 'Chicago'])
                return f"Employees in Chicago: {count}"
    
    # Highest/Lowest queries
    elif 'highest' in question:
        if 'salary' in question:
            max_salary = df['Salary'].max()
            emp_with_max = df[df['Salary'] == max_salary].iloc[0]
            return f"Highest salary: ${max_salary} (ID: {emp_with_max['ID']}, Name: {emp_with_max['Name']})"
        elif 'performance' in question:
            max_perf = df['Performance Score'].max()
            emp_with_max = df[df['Performance Score'] == max_perf].iloc[0]
            return f"Highest performance score: {max_perf} (ID: {emp_with_max['ID']}, Name: {emp_with_max['Name']})"
    
    elif 'lowest' in question:
        if 'salary' in question:
            min_salary = df['Salary'].min()
            emp_with_min = df[df['Salary'] == min_salary].iloc[0]
            return f"Lowest salary: ${min_salary} (ID: {emp_with_min['ID']}, Name: {emp_with_min['Name']})"
    
    # Total queries
    elif 'total' in question:
        if 'employees' in question:
            total = len(df)
            return f"Total employees: {total}"
    
    # Gender distribution
    elif 'gender' in question:
        if 'how many' in question:
            if 'male' in question:
                male_count = len(df[df['Gender'] == 'Male'])
                return f"Male employees: {male_count}"
            elif 'female' in question:
                female_count = len(df[df['Gender'] == 'Female'])
                return f"Female employees: {female_count}"
            elif 'other' in question:
                other_count = len(df[df['Gender'] == 'Other'])
                return f"Other gender employees: {other_count}"
    
    # Session queries
    elif 'session' in question:
        if 'how many in' in question:
            if 'morning' in question:
                count = len(df[df['Session'] == 'Morning'])
                return f"Employees in Morning session: {count}"
            elif 'evening' in question:
                count = len(df[df['Session'] == 'Evening'])
                return f"Employees in Evening session: {count}"
            elif 'night' in question:
                count = len(df[df['Session'] == 'Night'])
                return f"Employees in Night session: {count}"
    
    return "I couldn't understand your question. Please try asking about: ID, name, salary, department, status, location, or general statistics."

# ========== STEP 4: CREATE ADD EMPLOYEE TAB ==========
def create_add_employee_tab():
    """Create interface for adding new employees"""
    st.header("➕ Add New Employee")
    
    with st.form("add_employee_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name*", placeholder="e.g., John Smith")
            age = st.number_input("Age*", min_value=18, max_value=70, value=30)
            gender = st.selectbox("Gender*", ["Male", "Female", "Other"])
            department = st.selectbox("Department*", ["HR", "IT", "Sales"])
        
        with col2:
            salary = st.number_input("Salary*", min_value=1000, max_value=100000, value=5000)
            location = st.selectbox("Location*", ["New York", "Los Angeles", "Chicago"])
            session = st.selectbox("Session*", ["Morning", "Evening", "Night"])
            status = st.selectbox("Status*", ["Active", "Inactive"])
        
        col3, col4 = st.columns(2)
        with col3:
            experience = st.number_input("Experience (years)*", min_value=0, max_value=50, value=5)
            performance_score = st.number_input("Performance Score (1-5)*", min_value=1, max_value=5, value=3)
        
        with col4:
            joining_date = st.date_input("Joining Date*", value=datetime.now())
            joining_date_str = joining_date.strftime('%d-%m-%Y')
        
        submitted = st.form_submit_button("Add Employee")
        
        if submitted:
            if not name:
                st.error("Please enter employee name")
                return
            
            # Prepare employee data
            employee_data = {
                'name': name,
                'age': int(age),
                'gender': gender,
                'department': department,
                'salary': int(salary),
                'joining_date': joining_date_str,
                'performance_score': int(performance_score),
                'experience': int(experience),
                'status': status,
                'location': location,
                'session': session
            }
            
            # Load current data to get max ID
            df = load_data()
            
            # Add new employee
            new_employee = add_new_employee(df, employee_data)
            
            # Clear cache to reload data
            st.cache_data.clear()
            
            st.success(f"✅ Employee '{name}' added successfully!")
            st.info(f"Assigned ID: {new_employee['ID']}")
            
            # Show preview
            with st.expander("View Added Employee Details"):
                st.json(new_employee)

# ========== STEP 5: CREATE MANAGE DATA TAB ==========
def create_manage_data_tab():
    """Tab for managing data"""
    st.header("⚙️ Manage Data")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Refresh & Clean Data"):
            df = refresh_data()
            st.success(f"✅ Data refreshed successfully!")
            st.info(f"Total employees: {len(df)}")
            
            # Show a quick preview
            with st.expander("View Data Preview"):
                st.dataframe(df.head(), use_container_width=True)
    
    with col2:
        if st.button("🗑️ Clear New Employees File"):
            if os.path.exists(NEW_DATA_FILE):
                # Create empty dataframe with columns
                empty_df = pd.DataFrame(columns=[
                    'ID', 'Name', 'Age', 'Gender', 'Department', 'Salary',
                    'Joining Date', 'Performance Score', 'Experience',
                    'Status', 'Location', 'Session'
                ])
                empty_df.to_csv(NEW_DATA_FILE, index=False)
                st.cache_data.clear()
                st.success("✅ New employees file cleared!")
                st.info("Cache cleared. Please refresh the data.")
    
    with col3:
        if st.button("📥 Export Clean Data"):
            df = load_data()
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Clean CSV",
                data=csv,
                file_name="clean_employee_data.csv",
                mime="text/csv",
                key="download_clean_csv"
            )
    
    # Show current file status
    st.subheader("📁 File Status")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if os.path.exists(ORIGINAL_DATA_FILE):
            df_original = pd.read_csv(ORIGINAL_DATA_FILE)
            # Clean original data
            df_original_clean = df_original.dropna(subset=['ID'], how='any')
            st.metric("Original File", f"{len(df_original_clean)} records")
        else:
            st.error("Original file not found!")
    
    with col2:
        if os.path.exists(NEW_DATA_FILE):
            df_new = pd.read_csv(NEW_DATA_FILE)
            # Clean new data - remove empty rows
            df_new_clean = df_new.dropna(how='all')
            df_new_clean = df_new_clean.dropna(subset=['ID'], how='any')
            st.metric("New Employees File", f"{len(df_new_clean)} records")
        else:
            st.warning("New employees file not found!")
    
    with col3:
        df_combined = load_data()
        st.metric("Combined Data", f"{len(df_combined)} records")
    
    # Data cleaning options
    st.subheader("🔧 Data Cleaning Tools")
    
    if st.button("🛠️ Fix Data Issues"):
        df = load_data()
        
        # Check for duplicates
        duplicates = df[df.duplicated(subset=['ID'], keep=False)]
        
        if len(duplicates) > 0:
            st.warning(f"Found {len(duplicates)} duplicate IDs!")
            with st.expander("View Duplicates"):
                st.dataframe(duplicates, use_container_width=True)
            
            # Fix duplicates
            df_clean = df.drop_duplicates(subset=['ID'], keep='last')
            df_clean.to_csv('fixed_employee_data.csv', index=False)
            st.success(f"✅ Duplicates removed! Clean data saved to 'fixed_employee_data.csv'")
            st.info(f"Original: {len(df)} records | Clean: {len(df_clean)} records")
        else:
            st.success("✅ No duplicate IDs found!")
        
        # Check for missing data
        missing_names = df['Name'].isna().sum()
        missing_salary = df['Salary'].isna().sum()
        
        if missing_names > 0 or missing_salary > 0:
            st.warning(f"Found {missing_names} missing names and {missing_salary} missing salaries")
        else:
            st.success("✅ No critical missing data found!")

# ========== STEP 6: MAIN FUNCTION WITH TABS ==========
def main():
    st.set_page_config(
        page_title="Employee Data Chatbot", 
        page_icon="🤖",
        layout="wide"
    )
    
    # Create tabs - NOW WITH 4 TABS
    tab1, tab2, tab3, tab4 = st.tabs([
        "💬 Chat with Bot", 
        "➕ Add Employee", 
        "📊 View Data",
        "⚙️ Manage Data"  # NEW TAB
    ])
    
    with tab1:
        # Chatbot interface
        st.title("🤖 Employee Performance Data Chatbot")
        st.markdown("""
        Ask questions about the employee dataset. Examples:
        - "What is the salary of ID 25?"
        - "Tell me about Timothy Sanchez"
        - "How many employees are in HR department?"
        - "What is the average salary?"
        - "Who has the highest performance score?"
        - "How many active employees are there?"
        """)
        
        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask a question about the employee data:"):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Load current data (including new employees)
            df = load_data()
            
            # Process question and get response
            response = process_question(prompt, df)
            
            # Display assistant response
            with st.chat_message("assistant"):
                st.markdown(response)
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
    
    with tab2:
        # Add employee interface
        create_add_employee_tab()
    
    with tab3:
        # Data viewing interface with refresh button
        st.header("📊 View All Employee Data")
        
        # Add refresh button at the top
        if st.button("🔄 Refresh Data", key="refresh_view_tab"):
            df = refresh_data()
            st.success("Data refreshed!")
        else:
            df = load_data()
        
        # Show statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Employees", len(df))
        with col2:
            active_count = len(df[df['Status'] == 'Active'])
            st.metric("Active Employees", active_count)
        with col3:
            avg_salary = df['Salary'].mean()
            st.metric("Average Salary", f"${avg_salary:,.0f}")
        with col4:
            avg_perf = df['Performance Score'].mean()
            st.metric("Avg Performance", f"{avg_perf:.1f}/5")
        
        # Search and filter
        st.subheader("Search and Filter")
        search_col1, search_col2, search_col3 = st.columns(3)
        
        with search_col1:
            search_name = st.text_input("Search by Name")
        with search_col2:
            department_filter = st.multiselect(
                "Filter by Department",
                options=df['Department'].unique(),
                default=[]
            )
        with search_col3:
            status_filter = st.multiselect(
                "Filter by Status",
                options=df['Status'].unique(),
                default=['Active']
            )
        
        # Apply filters
        filtered_df = df.copy()
        if search_name:
            filtered_df = filtered_df[filtered_df['Name'].str.contains(search_name, case=False, na=False)]
        if department_filter:
            filtered_df = filtered_df[filtered_df['Department'].isin(department_filter)]
        if status_filter:
            filtered_df = filtered_df[filtered_df['Status'].isin(status_filter)]
        
        # Display data
        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "ID": st.column_config.NumberColumn(width="small"),
                "Name": st.column_config.TextColumn(width="medium"),
                "Salary": st.column_config.NumberColumn(
                    format="$%d"
                ),
                "Performance Score": st.column_config.ProgressColumn(
                    format="%f",
                    min_value=1,
                    max_value=5
                )
            }
        )
        
        # Download option
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=csv,
            file_name=f"employee_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    with tab4:  # NEW TAB
        # Manage data interface
        create_manage_data_tab()
def chatbot_answer(user_question):
    """
    This is the ONLY function UiPath calls
    """
    df = load_data()

    if df.empty:
        return "Employee data file not found or empty."

    return process_question(user_question, df)

# ========== RUN THE APPLICATION ==========
if __name__ == "__main__":
    main()