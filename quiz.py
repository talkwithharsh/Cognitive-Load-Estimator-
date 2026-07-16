from flask import Flask, request, jsonify, render_template_string
from database import save_quiz_response, DB_PATH
import sqlite3, time, uuid

app = Flask(__name__)

# Sample question bank — replace with real questions
QUESTIONS = {
    'easy': [
        {'id': 1, 'text': 'What does AI stand for?',
        'options': ['Artificial Intelligence', 'Auto Input', 'Automated Interface', 'None'],
        'answer': 0},
        {'id': 2, 'text': 'Which language is used for ML?',
        'options': ['HTML', 'Python', 'CSS', 'Excel'],
        'answer': 1},
    ],
    'medium': [
        {'id': 3, 'text': 'What is overfitting in ML?',
        'options': ['Model too complex', 'Model too simple', 'Low accuracy', 'Fast training'],
        'answer': 0},
    ],
    'hard': [
        {'id': 4, 'text': 'What does gradient descent minimise?',
        'options': ['Loss function', 'Accuracy', 'Epoch count', 'Layer depth'],
        'answer': 0},
    ]
}

# Track when each question was shown
question_start_times = {}

@app.route('/question/<difficulty>/<int:index>')
def get_question(difficulty, index):
    '''Return question at given index for given difficulty'''
    questions = QUESTIONS.get(difficulty, [])
    if index >= len(questions):
        return jsonify({'done': True})

    q = questions[index].copy()
    q.pop('answer')   # never send answer to browser!

    # Record when this question was shown
    key = f'{difficulty}_{index}'
    question_start_times[key] = time.time()

    return jsonify(q)


@app.route('/answer', methods=['POST'])
def submit_answer():
    '''Receives student's answer and logs timing'''
    data = request.json
    session_id  = data['session_id']
    difficulty  = data['difficulty']
    index       = data['index']
    chosen      = data['chosen_option']   # 0,1,2,3
    confidence  = data['confidence']       # 1-5

    # Calculate response time
    key = f'{difficulty}_{index}'
    start = question_start_times.get(key, time.time())
    response_time = round(time.time() - start, 2)

    # Check if correct
    correct_answer = QUESTIONS[difficulty][index]['answer']
    is_correct = (chosen == correct_answer)

    # Save to database
    save_quiz_response(
        session_id=session_id,
        question_id=QUESTIONS[difficulty][index]['id'],
        response_time=response_time,
        is_correct=is_correct,
        confidence=confidence
    )

    return jsonify({
        'response_time': response_time,
        'is_correct': is_correct,
        'correct_answer': correct_answer
    })


if __name__ == '__main__':
    app.run(port=5002, debug=True)