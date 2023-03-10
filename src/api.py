from flask import Flask, render_template, request, flash, redirect, send_file
from werkzeug.utils import secure_filename
from pathlib import Path
from run_queue import RunQueue
from typing import Dict
from datetime import datetime
from threading import Thread
import subprocess
import runner
import uuid

from runner import RunRequest, RunResult


app = Flask("pmu-service", template_folder='src/html')

# Obviously need to change this if deployed
app.secret_key = 'very secure'

# 32 MB upload size limit
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024
UPLOAD_PATH = Path("uploads")


run_queue = RunQueue()
run_results: Dict[str, RunResult] = {}

currently_running: str = ""
running_start: datetime = datetime.now()


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        # POST
        if 'file' not in request.files:
            flash('Missing file part')
            return redirect(request.url)
        file = request.files['file']
        if file is None or file.filename == '':
            flash('No file selected')
            return redirect(request.url)

        file_path = UPLOAD_PATH / secure_filename(file.filename)
        file.save(file_path)
        id = str(uuid.uuid4())
        run_queue.put(RunRequest(id, file_path))

        return redirect('query/' + id)


@app.route('/query/<id>', methods=['GET'])
def success(id: str):
    if id in run_results:
        res = run_results[id]
        if res.error:
            return render_template('query.html', msg='Encountered an error trying to run your program\n')
        else:
            return send_file(res.output_file)
    elif currently_running == id:
        return render_template('query.html', msg='Your program is currently running', id=id)
    else:
        pos = run_queue.positionOf(lambda r: r.id == id) 
        if pos is None:
            return render_template('query.html', msg='Invalid id', id=id)
        else:
            return render_template('query.html', msg=f'Your program is {pos[0]}/{pos[1]} in the queue.', id=id)


def runner_thread():
    print("Runner thread started")
    global currently_running
    global running_start
    while True:
        next_req = run_queue.get()
        currently_running = next_req.id
        running_start = datetime.now()
        result = runner.run(next_req)
        if result.error:
            print(result.err_msg)
        run_results[next_req.id] = result
        print(f"finished running {next_req.id}")

if __name__ == '__main__':
    # Make sure upload directory exists
    subprocess.check_call(["mkdir", "-p", str(UPLOAD_PATH)])

    # Initialize runner
    runner.init()

    t = Thread(target=runner_thread)
    t.start()
    app.run()
