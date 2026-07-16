import sqlite3, pandas as pd
from database import DB_PATH

def build_dataset():
    conn = sqlite3.connect(DB_PATH)

    # Load all labelled sessions
    sessions = pd.read_sql(
        'SELECT * FROM sessions WHERE load_class IS NOT NULL', conn)
    print(f'Total labelled sessions: {len(sessions)}')
    print('Class distribution:')
    print(sessions['load_class'].value_counts())

    rows = []
    for _, session in sessions.iterrows():
        sid = session['id']

        # Get average CV signals for this session
        cv = pd.read_sql(
            f"SELECT * FROM cv_signals WHERE session_id='{sid}'", conn)

        # Get average behaviour signals
        beh = pd.read_sql(
            f"SELECT * FROM behaviour_signals WHERE session_id='{sid}'", conn)

        # Get quiz signals (average response time and confidence)
        quiz = pd.read_sql(
            f"SELECT * FROM quiz_responses WHERE session_id='{sid}'", conn)

        if cv.empty or beh.empty or quiz.empty:
            print(f'Skipping session {sid} — incomplete data')
            continue

        # Map expression to number: NEUTRAL=0, CONFUSED=1, FOCUSED=2
        expr_map = {'NEUTRAL': 0, 'CONFUSED': 1, 'FOCUSED': 2}
        gaze_map = {'CENTER': 0, 'LEFT': 1, 'RIGHT': 1}

        row = {
            'session_id'      : sid,
            'blink_rate'      : cv['blink_rate'].mean(),
            'gaze_score'      : cv['gaze'].map(gaze_map).mean(),
            'expression'      : cv['expression'].map(expr_map).mean(),
            'wpm'             : beh['wpm'].mean(),
            'backspace_rate'  : beh['backspace_rate'].mean(),
            'scroll_reversals': beh['scroll_reversals'].mean(),
            'mouse_idle'      : beh['mouse_idle'].mean(),
            'response_time'   : quiz['response_time'].mean(),
            'confidence'      : quiz['confidence'].mean(),
            'load_label'      : session['load_class']
        }
        rows.append(row)

    df = pd.DataFrame(rows)
    df = df.dropna()   # remove any rows with missing data

    # Save
    df.to_csv('../dataset/training_dataset.csv', index=False)
    print(f'Dataset saved: {len(df)} rows')
    print(df.head())
    return df

if __name__ == '__main__':
    build_dataset()
