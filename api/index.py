from app import app

@app.route('/api')
def api():
    return 'API is working'


