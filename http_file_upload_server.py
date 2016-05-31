import os
from flask import Flask, request, redirect, url_for, make_response, jsonify, abort
from werkzeug import secure_filename
from functools import wraps


UPLOAD_FOLDER = '/tmp/UPLOADED/'
ALLOWED_EXTENSIONS = set(['txt', 'mp4'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

chaves = {}

@app.route("/401NotFound", methods=['GET', 'POST'])
def intertcetor(func):
    def retorno401(*args, **kwargs):
        content = {'please move along': 'nothing to see here'}
        # return make_response(content, 401)
        return abort(401)
    def inner(*args, **kwargs): #1
        print "Arguments were: %s, %s" % (args, kwargs)
        auth = str(request.headers.get('Authorization'))
        if (auth):
            if (chaves.get(auth)):
                print("Auth %s" % (chaves.get(auth)))
                return func(*args, **kwargs) #2

        return retorno401(*args, **kwargs)

        # return lambda *args, **kargs: content, 401


    return inner

@app.route("/", methods=['GET', 'POST'])
def index():
    print(request.method)
    if request.method == 'POST':
        print(request)
        print(dir(request))
        file = request.files['file']
        print(file)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('index'))
    return """
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    <p>%s</p>
    """ % "<br>".join(os.listdir(app.config['UPLOAD_FOLDER'],))

@app.route("/auth/local", methods=["POST"])
def login():
    content = request.json
    print(content)
    email = str(content['email'])
    # if
    tokenStr = token= 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJfaWQiOiI1NzM5ZmQzNWM2NjcwYTNhNTUxMjM1YjMiLCJyb2xlIjoidXNlciIsImlhdCI6MTQ2MzQyMDI2MSwiZXhwIjoxNDYzNDc0MjYxfQ.v3tRB9B-MK2Ev-B0_0mGkeddDZa59JKdVFUJngWwgNc'
    chaves["Bearer %s" % tokenStr] = email
    return jsonify(
        token= tokenStr
    )

@app.route("/api/videos/<videoMotoraId>", methods=["GET"])
@app.route("/api/videos/<videoMotoraId>/cut/<ini>/<fim>", methods=["GET"])
@intertcetor
def video(videoMotoraId, ini=None, fim=None):
    print "videomotoraId: %s" % videoMotoraId
    print "ini: %s" % ini
    print "fim: %s" % fim
    return jsonify({'url': 'http://159.203.66.252:3000/uploads/573a0fabc6670a3a551235bc/21206_1460836329000_1460836389975_5_10.mp4'})




if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)