from flask import Flask, render_template, request, jsonify
import hashlib
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_content TEXT NOT NULL,
            data_hash TEXT UNIQUE NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def generate_hash(content):
    return hashlib.sha256(content.strip().encode('utf-8')).hexdigest()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_data', methods=['POST'])
def add_data():
    content = request.form.get('content')
    if not content:
        return jsonify({'status': 'error', 'message': 'Empty input!'}), 400

    content_hash = generate_hash(content)

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM records WHERE data_hash = ?', (content_hash,))
    existing_entry = cursor.fetchone()

    if existing_entry:
        conn.close()
        return jsonify({
            'status': 'redundant',
            'message': 'Duplicate data detected! Entry rejected.'
        }), 409

    cursor.execute('INSERT INTO records (data_content, data_hash) VALUES (?, ?)', (content, content_hash))
    conn.commit()
    conn.close()

    return jsonify({
        'status': 'success',
        'message': 'Unique data successfully added to database!'
    }), 201

@app.route('/get_records', methods=['GET'])
def get_records():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, data_content, data_hash FROM records')
    rows = cursor.fetchall()
    conn.close()
    return jsonify({'records': rows})

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)