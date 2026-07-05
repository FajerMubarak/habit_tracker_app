import pandas as pd 
import datetime

def read_file():
    df= pd.read_csv('habitsFile.csv')
    return df 
    
def add_habit(habit, frequency, goal, category, start_date , total_days):
    df = read_file()
    new_habit ={'Habit' : habit ,
                'Frequency' : frequency ,
                'Goal':goal ,
                'Category':category  ,
                'Start Date':start_date,
                'Completed': False,
                'Last Completed': '',
                'Streak': 0,
                'Best Streak': 0,
                'Total Completions': 0,
                'Total Days': total_days }

    df = pd.concat([df, pd.DataFrame([new_habit])] , ignore_index=True)
    df.to_csv("habitsFile.csv", index=False)


def complete_habit(habit):
    df = read_file()

    if 'Last Completed' in df.columns:
        df['Last Completed'] = df['Last Completed'].astype(str).replace('nan', '')

    today = str(datetime.date.today())
    yesterday = str(datetime.date.today() - datetime.timedelta(days=1))
    condition = df['Habit'] == habit

    if condition.any():
        val_streak = df.loc[condition, 'Streak'].values[0]
        val_best_streak = df.loc[condition, 'Best Streak'].values[0]
        val_total_completions = df.loc[condition, 'Total Completions'].values[0]
        
        
        streak = int(val_streak) if pd.notna(val_streak) and str(val_streak).strip() != "" and str(val_streak) != "nan" else 0
        best_streak = int(val_best_streak) if pd.notna(val_best_streak) and str(val_best_streak).strip() != "" and str(val_best_streak) != "nan" else 0
        total_completions = int(val_total_completions) if pd.notna(val_total_completions) and str(val_total_completions).strip() != "" and  str(val_total_completions) != "nan" else 0
        
        all_dates = str(df.loc[condition, 'Last Completed'].values[0]).strip()
        if all_dates == "" or all_dates == "nan":
            last_completed_date = ""
        else:
            last_completed_date = all_dates.split(",")[-1].strip()
        if last_completed_date == today:
            return "You have already completed this habit today!"
        elif last_completed_date == yesterday:
            new_streak = streak + 1
        else:
            new_streak = 1

        if all_dates == "":
            updated_dates = today
        else:
            updated_dates = all_dates + "," + today

        df.loc[condition, 'Streak'] = new_streak
        df.loc[condition, 'Last Completed'] = updated_dates
        df.loc[condition, 'Total Completions'] = total_completions + 1

        if 'Completed' in df.columns:
            df.loc[condition, 'Completed'] = True

        if new_streak > best_streak:
            df.loc[condition, 'Best Streak'] = new_streak

        df.to_csv("habitsFile.csv", index=False)
        return "Habit logged successfully!"

    return "Habit not found."


def show_statistics():
    df = read_file()

    if df.empty:
        print("No statistics available yet. Add habits first!")
        return

    df['Completion Rate'] = (df['Total Completions'] / df['Total Days'].replace(0, 1)) * 100

    rewards = []

    for streak in df["Streak"]:
        if streak >= 100:
            rewards.append("🥇 Gold")
        elif streak >= 30:
            rewards.append("🥈 Silver")
        elif streak >= 7:
            rewards.append("🥉 Bronze")
        else:
            rewards.append("No Reward")

    df['Reward'] = rewards

    statistics_df = df[['Habit', 'Streak', 'Best Streak', 'Completion Rate','Reward']]

    return statistics_df


def delete_habit(habit):
    df = read_file()
    df = df[df['Habit'] != habit]
    df.to_csv("habitsFile.csv", index=False)
    


def edit_habit(old_habit ,new_habit= None, new_frequency= None , new_goal= None , new_category= None , new_start_date=None , new_total_days=None ):

    df = read_file()
    condition = df['Habit'] == old_habit
    
    if new_habit is not None:
        df.loc[condition, 'Habit'] = new_habit
    if new_frequency is not None:
        df.loc[condition, 'Frequency'] = new_frequency
    if new_goal is not None:
        df.loc[condition, 'Goal'] = new_goal
    if new_category is not None:
        df.loc[condition, 'Category'] = new_category
    if new_start_date is not None:
        df.loc[condition, 'Start Date'] = new_start_date
    if new_total_days is not None:
        df.loc[condition, 'Total Days'] = new_total_days

    df.to_csv("habitsFile.csv", index=False)



def get_habit_dates():
    df = read_file()
    if df.empty:
        return []
    all_series = df['Last Completed'].astype(str).str.strip()
    clean_series = all_series[(all_series != "") & (all_series != "nan")]
    if clean_series.empty:
        return []
    all_series = clean_series.str.split(',').explode()
    all_series = all_series.str.strip()
    dates_list = pd.to_datetime(all_series, errors='coerce').dt.date.dropna().tolist()
    return list(set(dates_list))

def get_data():
    df = read_file()
    if df.empty:
        return pd.DataFrame()
    view_columns = ['Habit', 'Category', 'Frequency', 'Goal', 'Streak', 'Best Streak', 'Total Days']
    display_df = df[view_columns].copy()
    return display_df

    

def best_time():
    df = read_file()

    if df.empty:
        return "No data available"

    times = []

    for value in df["Last Completed"]:
        if pd.isna(value) or value == "":
            continue
            
        last = str(value).split(",")[-1]
        hour = pd.to_datetime(last).hour
        times.append(hour)

    if len(times) == 0:
        return "No completion history"

    average = sum(times) / len(times)

    if average < 12:
        return "🌅 Morning"
    elif average < 18:
        return "☀️ Afternoon"
    else:
        return "🌙 Evening"


def suggest_habit_stack():
    df = read_file()

    if len(df) < 2:
        return "Add at least two habits to get suggestions."

    df = df.sort_values(by="Streak", ascending=False)

    main_habit = df.iloc[0]["Habit"]

    if df.iloc[0]["Streak"] == 0:
        return "Complete your habits for a few days to receive suggestions."

    other_habits = df[df["Habit"] != main_habit]
    random_habit = other_habits.sample(1).iloc[0]["Habit"]

    return f"💡 You are very consistent with '{main_habit}'. Try doing '{random_habit}' immediately after it to build a stronger routine."