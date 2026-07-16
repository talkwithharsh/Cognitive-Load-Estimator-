from flask import Flask, request, jsonify, render_template_string
from database import save_nasa_tlx

app = Flask(__name__)

NASA_FORM = '''
<!DOCTYPE html><html><body style='font-family:Arial;max-width:600px;margin:40px auto'>
<h2>Session Complete — Please Rate Your Experience</h2>
<p>Move each slider to rate how you felt during this study session (0 = Low, 20 = High)</p>
<form id='tlxForm'>
<label>Mental Demand (how hard did you think?)</label><br>
<input type='range' name='mental' min='0' max='20' value='10'><br><br>
<label>Physical Demand (physical effort required?)</label><br>
<input type='range' name='physical' min='0' max='20' value='5'><br><br>
<label>Temporal Demand (how rushed did you feel?)</label><br>
<input type='range' name='temporal' min='0' max='20' value='10'><br><br>
<label>Performance (how well did you do?)</label><br>
<input type='range' name='performance' min='0' max='20' value='10'><br><br>
<label>Effort (how hard did you work?)</label><br>
<input type='range' name='effort' min='0' max='20' value='10'><br><br>
<label>Frustration (how stressed did you feel?)</label><br>
<input type='range' name='frustration' min='0' max='20' value='5'><br><br>
<input type='hidden' name='session_id' value='{{ session_id }}'>
<button type='button' onclick='submitForm()'>Submit</button>
</form>
<div id='result'></div>
<script>
function submitForm() {
const form = document.getElementById('tlxForm');
const data = { session_id: form.session_id.value,
    mental: +form.mental.value, physical: +form.physical.value,
    temporal: +form.temporal.value, performance: +form.performance.value,
    effort: +form.effort.value, frustration: +form.frustration.value };
fetch('/submit_tlx', {method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify(data)}).then(r=>r.json()).then(d=>{
    document.getElementById('result').innerHTML =
    '<h3>Thank you! Your load score: ' + d.nasa_score.toFixed(1) + '/100 (' + d.load_class + ')</h3>';
});
}
</script></body></html>
'''

@app.route('/tlx/<session_id>')
def show_tlx(session_id):
    return render_template_string(NASA_FORM, session_id=session_id)

@app.route('/submit_tlx', methods=['POST'])
def submit_tlx():
    data = request.json
    session_id = data.pop('session_id')
    nasa_score, load_class = save_nasa_tlx(session_id, data)
    return jsonify({'nasa_score': nasa_score, 'load_class': load_class})

if __name__ == '__main__':
 app.run(port=5003, debug=True)