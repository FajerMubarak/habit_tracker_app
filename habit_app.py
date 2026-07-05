import streamlit as st 
import habit_function as hf
import pandas as pd
import datetime
from streamlit_calendar import calendar

st. title('Habit Tracker')

with st.sidebar:
    add_radio = st.radio('Choose ',
        ['🏠 Dashboard',
         '➕ Add New Habit', 
        '✅ Log Completion' , 
        '📊 Analytics & Insights',  
        '✏️ Modify Habits',
        '❌ Delete Habits',
        '📋 View All Habits'  ]    )

df =hf.read_file()

if add_radio == '🏠 Dashboard':
        
    dates = hf.get_habit_dates()
    if not dates:
        st.warning("You haven't logged any completions yet! Go to 'Log completion' to start.")
    else:
        st.subheader("🗓️ Habit Completion Calendar View")
        events= []
        for d in dates:
            events.append({
            "title": "Completed",
            "start": str(d),
                "end": str(d)})

    calendar(events=events)
    st.markdown("---")
    today = str(datetime.date.today())

    for i, row in df.iterrows():
        last_completed = str(row["Last Completed"])

        if today not in last_completed:
            st.toast(f"🔔 Reminder: Don't forget to complete '{row['Habit']}' today!")


           
elif add_radio == '➕ Add New Habit' :
    st.subheader("✨ Create a New Positive Habit")
    st.markdown("Fill in the details below to start tracking your new routine and building your streak!")
    st.markdown("---")
    habit = st.text_input("New Habit Name")
    frequency =st.selectbox("Frequency", ["Daily", "Weekly", "Monthly"])
    goal=st.number_input("Insert a goal",min_value=1, value=1)
    category =st.selectbox("Choose Category:",[ "Education & Study","Health & Fitness","Mental Wellbeing","Productivity & Work","Daily Routine"])
    start_date = st.date_input("Start Date", value=datetime.date.today())
    total_days=st.number_input("Insert a number of days ",min_value=1, value=30)

    if st.button('Add Habit'): 
        if habit.strip() == "" or category.strip() == "":
            st.error("Please fill in both the Habit Name and Category before saving!", icon="⚠️")
        else:
            hf.add_habit(habit,frequency,goal,category, str(start_date) ,  total_days)
            st.success('Habit Added Successfully', icon="✅")
       


elif add_radio == '✅ Log Completion' :
    st.subheader("🔥 Daily Habit Check-In")
    st.markdown("Track your progress for today! Select a habit you've finished and log it to keep your streak alive.")
    st.markdown("---")
    
    if df.empty:
        st.info("No habits found to log! Add some habits first.")
    else:
        today = str(datetime.date.today())
        active_habits = df[~df['Last Completed'].astype(str).str.contains(today)]
        
        if active_habits.empty:
            st.balloons()
            st.success("🎉 Awesome! You've completed all your habits for today!")
        else:
            habit = st.selectbox('🎯 Choose a habit to log today:',active_habits["Habit"])
    
            if st.button('Complete Habit'):  
                message = hf.complete_habit(habit)
                if "You have already completed this habit today!" in message:
                    st.warning(message, icon="⚠️")
                else:
                    st.success(f"Great job! '{habit}' logged successfully. Streak updated! 🔥", icon="✅")

                    st.markdown("### 💡 Need an Idea? Try Habit Stacking!")
                    st.success(hf.suggest_habit_stack())
        
elif add_radio == '📊 Analytics & Insights' :
    st.subheader("📊 Performance & Statistics Dashboard")
    st.markdown("Monitor your consistency, track your best streaks, and see what rewards you've unlocked!")
    st.markdown("---")
    optimal_period = hf.best_time()
    if "No" not in optimal_period:
        st.info(f"⚡ **Keep it up!** You are most active during the **{optimal_period}**. Try to log your habits around this time!")
    else:
        st.info("🌱 **Welcome!** Start logging your habits to track your peak performance times.")
        
    result= hf.show_statistics()
    if result is None or result.empty:
        st.info("No statistics available yet. Add habits first", icon="ℹ️")
    else:
        st.dataframe(result , use_container_width=True)

elif add_radio == '✏️ Modify Habits' :
    st.subheader("📝 Edit Existing Habits")
    st.markdown("Modify the details, frequency, or goals of your current habits instantly.")
    st.markdown("---")
    if df.empty:
        st.info("No habits found to edit!")
    else:
        old_habit = st.selectbox("Select a habit to edit:", df["Habit"])
    
        habit_data = df[df['Habit'] == old_habit].iloc[0]
        
        st.markdown(f"### ⚙️ Modifying: **{old_habit}**")
        st.subheader(f"Editing: {old_habit}")
    
        new_name = st.text_input("Habit Name", value=str(habit_data['Habit']))
        options = ["Daily", "Weekly", "Monthly"]
        new_freq = st.selectbox("Frequency", options,index=options.index(habit_data["Frequency"]))
                                
        new_goal = st.number_input("Goal", value=int(habit_data['Goal']))
        new_category = st.text_input("Category", value=str(habit_data['Category']))
        new_start = st.date_input("Start Date", value=pd.to_datetime(habit_data['Start Date']).date())

        total_days_value = 0 if pd.isna(habit_data['Total Days']) else int(habit_data['Total Days'])
        new_total = st.number_input("Total Days", value= total_days_value)

        if st.button("Save Changes"):
            hf.edit_habit(old_habit=old_habit,  new_habit = new_name, new_frequency=new_freq, new_goal=new_goal, new_category=new_category,     new_start_date=str(new_start), new_total_days= new_total )
            st.success(f"'{old_habit}' updated successfully!", icon="✨")
            

elif add_radio == '❌ Delete Habits' :
    st.subheader("🗑️ Remove Habits")
    st.markdown("Careful! Deleting a habit will permanently erase its entire progress history, streaks, and statistics.")
    st.markdown("---")
    if df.empty:
        st.info("No habits found to remove!")
    else:
         habit_to_delete = st.selectbox("Select a habit to delete:", df["Habit"])
         if st.button('Delete Habit'):
            hf.delete_habit(habit_to_delete)
            st.success(f"'{habit_to_delete}' Deleted Successfully", icon="🗑️")
            



elif add_radio == '📋 View All Habits' :
    st.subheader("📋 My Habits Registry")
    st.markdown("---")
    
    clean_df = hf.get_data()
    
    if clean_df.empty:
        st.info("Your habit list is empty! Add some habits first.", icon="ℹ️")
    else:
         st.dataframe(clean_df, use_container_width=True, hide_index=True)