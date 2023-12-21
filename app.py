from chalice import Chalice

app = Chalice(app_name='video-translator')


@app.route('/')
def index():
    return {'hello': 'world'}

