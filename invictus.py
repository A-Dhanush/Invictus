import subprocess
import requests
import json
import os
import re

# Function to remove ANSI escape codes from text
def remove_ansi_escape_codes(text):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)


def cms_find(param, key):
    url = f'https://whatcms.org/APIEndpoint/Technology?key={key}&url={param}'
    r = requests.get(url)
    var = r.json()
    
    if 'results' in var and var['results']:
        cms_name = var['results'][0]['name']
    else:
        cms_name = "No support for CMS"

    return cms_name

def cms_scan(cms_name, param):
    sanitized_param = "".join(c for c in param if c.isalnum() or c in ('-', '_'))
    file_path = os.path.join(os.path.dirname(__file__), 'reports', f"cms_scan_{sanitized_param}.txt")
    
    scan_output = ""

    try:
        if cms_name:
            cms = f"CMS Detected: {cms_name}"
            with open(file_path, "w") as f:
                f.write(cms)
            if cms_name == "WordPress":
                print ("!---Starting WordPress Scan---!")
                scan_output = subprocess.check_output(["wpscan", "--url", param, "--no-banner", "--random-user-agent", "aggressive"], stderr=subprocess.STDOUT)
            elif cms_name == "Joomla":
                print ("!---Starting Joomla Scan---!")
                scan_output = subprocess.check_output(["perl", "joomscan.pl", "-u", param], cwd="/Invictus/Tools/joomscan", stderr=subprocess.STDOUT)
            elif cms_name == "Drupal":
                print ("!---Starting Drupal Scan---!")
                scan_output = subprocess.check_output(["droopescan", "scan", "drupal", "-u", param], stderr=subprocess.STDOUT)
            else:
                no_supp = "No support for CMS yet."
                with open(file_path, "a") as f:
                    f.write(no_supp)
                return no_supp
        else:
            no_supp = "No support for CMS yet."
            with open(file_path, "w") as f:
                f.write(no_supp)
            return no_supp

        # Check if scan_output is bytes and convert it to a string
        if isinstance(scan_output, bytes):
            scan_output = scan_output.decode('utf-8')

        # Remove ANSI escape codes from the scan output
        scan_output = remove_ansi_escape_codes(scan_output)

        with open(file_path, "a") as f:
            # Write the plain text scan results to the file
            f.write(scan_output)

        # Read and return the scan results from the file
        with open(file_path, "r") as f:
            scan_results = f.read()

        print("Scan Results:")
        print(scan_results)  # Add this line for debugging
        return scan_results
    except Exception as e:
        # Handle exceptions gracefully and log the error
        print(f"Error: {str(e)}")
        return str(e)
