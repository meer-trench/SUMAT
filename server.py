import http.server
import socketserver
import urllib.parse
import os
import time
import json
import subprocess
#import argparse
from io import BytesIO
import webbrowser
PORT = 8000
BASE_DIR = 'tasks'
LOG_FILE = 'submit.log'

#parser = argparse.ArgumentParser(description="Run Snakemake with specified cores.")
#parser.add_argument('--cores', type=int, required=True, help='Number of cores to use')
#args = parser.parse_args()

if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/submit':
            self.handle_submit()
        else:
            self.send_error(404, "File not found")

    def do_GET(self):
        if self.path == '/taskids':
            self.handle_taskids()
        elif self.path.startswith('/query'):
            self.handle_query()
        else:
            super().do_GET()

    def handle_submit(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        
        content_type = self.headers['Content-Type']
        boundary = content_type.split("=")[1].encode()
        parts = body.split(b'--' + boundary + b'\r\n')

        form_data = {}
        file_data = None
        file_name = None

        for part in parts:
            if b'Content-Disposition' in part:
                headers, content = part.split(b'\r\n\r\n', 1)
                headers = headers.decode()
                content = content.rstrip(b'\r\n')
                disposition = headers.split(';')
                name = disposition[1].split('=')[1].strip('"')
                if 'filename' in headers:
                    file_name = disposition[2].split('=')[1].strip('"')
                    file_data = content
                else:
                    if name in form_data:
                        form_data[name] = form_data[name] + "," + content.decode()
                    else:
                        form_data[name] = content.decode()

        # if not file_name.endswith('.tsv'):
        #     self.send_response(400)
        #     self.end_headers()
        #     self.wfile.write(b'Error: Uploaded file must be a .tsv file.')
        #     return

        task_id = str(int(time.time()))[-8:]
        project_path = os.path.join(form_data['location'], task_id)
        os.makedirs(project_path, exist_ok=True)
        with open(os.path.join(project_path, 'metadata.tsv'), 'ab') as metadata_file:
            metadata_file.write(file_data)
        p1=subprocess.Popen(['python scripts/init.py %s/metadata.tsv -l %s' % (project_path,project_path)], shell =True)
        p1.wait()
        #print(cores)
        config_content = f"""
diversity: {form_data['diversity']}
novelty: {form_data['novelty']}
resources: {form_data['resources']}
checkm_db: {form_data['checkm_db']}
mp_db: {form_data['mp_db']}
kraken2_db: {form_data['kraken2_db']}
adapter1: {form_data['adapter1']}
adapter2: {form_data['adapter2']}
location: {project_path}
"""
        with open(os.path.join(project_path, 'config.yaml'), 'a') as config_file:
            config_file.write(config_content)

        #with open(os.path.join(project_path, 'metadata.tsv'), 'ab') as metadata_file:
        #    metadata_file.write(file_data)

        targets = form_data.get('target', '').split(',')
        #cores = subprocess.Popen(['python', f"scripts/init.py {project_path}/metadata.tsv -l {project_path}"])
        subprocess.Popen(['python scripts/allocate_runs_to_samples.py -i %s/metadata_new.tsv -d %s -r %s/raw_data -l %s/allo.log' % (project_path,project_path,project_path,project_path)],shell=True)
        #print(form_data)
        if 'profiling' in targets and 'denovo_assembly' in targets:
            run_content = f"snakemake --snakefile test.smk --configfile {project_path}/config.yaml --rerun-incomplete --jobs 50  --latency-wait 360 --printshellcmds --until all"
        elif 'profiling' in targets:
            run_content = f"snakemake --snakefile test.smk --configfile {project_path}/config.yaml --rerun-incomplete --jobs 50  --latency-wait 360 --printshellcmds --until target_profile"
        elif 'denovo_assembly' in targets:
            run_content = f"snakemake --snakefile test.smk --configfile {project_path}/config.yaml --rerun-incomplete --jobs 50 --latency-wait 360 --printshellcmds --until target_mags"
        else:
            run_content = ""

        with open(os.path.join(project_path, 'run.sh'), 'w') as run_file:
            run_file.write(run_content)

        subprocess.Popen(['bash', os.path.join(project_path, 'run.sh')])

        with open(os.path.join(BASE_DIR, LOG_FILE), 'a') as log_file:
            log_file.write(f"{task_id},{project_path},{time.ctime()}\n")

        self.send_response(200)
        self.end_headers()
        self.wfile.write(f"Task {task_id} has started running.".encode())

    def handle_taskids(self):
        task_ids = []
        if os.path.exists(os.path.join(BASE_DIR, LOG_FILE)):
            with open(os.path.join(BASE_DIR, LOG_FILE), 'r') as log_file:
                for line in log_file:
                    task_id = line.split(',')[0]
                    task_ids.append(task_id)
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(task_ids).encode())

    def handle_query(self):
        query_components = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(query_components.query)
        task_id = query_params.get('taskid', [None])[0]

        if not task_id:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'Error: Task ID is required.')
            return

        project_path = None
        if os.path.exists(os.path.join(BASE_DIR, LOG_FILE)):
            with open(os.path.join(BASE_DIR, LOG_FILE), 'r') as log_file:
                for line in log_file:
                    if line.startswith(task_id):
                        project_path = line.split(',')[1]
                        break

        if not project_path:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Error: Task ID not found.')
            return

        log_path = os.path.join(project_path, 'snakemake.log')
        if not os.path.exists(log_path):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'status: running\nLog file not found.')
            return

        with open(log_path, 'r') as log_file:
            log_content = log_file.read()

        if 'Error' in log_content:
            status = 'Error'
            error_lines = [line for line in log_content.split('\n') if 'Error' in line]
            log_content = '\n'.join(error_lines)
        elif 'Complete' in log_content:
            status = 'Complete'
        else:
            status = 'running'

        self.send_response(200)
        self.end_headers()
        self.wfile.write(f"status: {status}\n{log_content}".encode())

with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()
    webbrowser.open(f"http://localhost:8080")
