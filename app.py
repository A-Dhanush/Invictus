from flask import Flask, render_template, request, flash, get_flashed_messages, redirect, url_for, send_file, jsonify
import invictus
from urllib.parse import quote
import os
from ansi2html import Ansi2HTMLConverter


app = Flask(__name__)
app.secret_key = 'invictusArmy'  # Replace with your own secret key
converter = Ansi2HTMLConverter()

@app.route('/')
def index():
    flash_messages = get_flashed_messages()
    return render_template('index.html', flash_messages=flash_messages)

@app.route('/scan', methods=['POST'])
def scan():
    
    try:
        param = request.form.get('website', '')
        key = ' YOUR KEY '  # Replace with your API key

        if not param:
            flash('Website URL is required.', 'error')
            return redirect(url_for('index'))
        # Step 1: Find CMS
        cms_name = invictus.cms_find(param, key)
        if cms_name:
            flash(f'CMS Detected : {cms_name}')
            # Step 2: Run scans according to CMS
            scan_results = invictus.cms_scan(cms_name, param)
            # Convert ANSI escape codes to HTML/CSS
            scan_results_html = converter.convert(scan_results, full=False)
            if scan_results:
                flash(f'Scan for {param} completed successfully.', 'success')
            else:
                flash(f'No scan results available for {param}.', 'warning')
        else:
            flash('CMS information not found for the given URL.', 'error')

    except Exception as e:
        flash(f'Error: {str(e)}', 'error')

    flash_messages = get_flashed_messages()

    # Render the scan results template
    return render_template('index.html', scan_results=scan_results_html, flash_messages=flash_messages)

@app.route('/download_report/<param>')
def download_report(param):
    sanitized_param = "".join(c for c in param if c.isalnum() or c in ('-', '_'))
    file_path = os.path.join(os.path.dirname(__file__), 'reports', f"cms_scan_{sanitized_param}.txt")

    if os.path.exists(file_path):
        encoded_param = quote(sanitized_param)
        return send_from_directory(os.path.dirname(file_path), f"cms_scan_{sanitized_param}.txt", as_attachment=True, download_name=f"cms_scan_{encoded_param}.txt")
    else:
        flash(f'Report file not found for {param}.', 'error')
        return redirect(url_for('index'))


