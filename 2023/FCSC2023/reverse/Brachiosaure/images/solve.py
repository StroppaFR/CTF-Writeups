import requests
import time
import subprocess
import re

URL = "https://brachiosaure.france-cybersecurity-challenge.fr/"

while True:
    # Don't get banned for bruteforcing !
    time.sleep(1)

    # Get the username from the webpage
    r = requests.get(URL)
    username = r.text.split('<h4 class="text-warning">')[1].split('</h4>')[0]
    print("Username:", username)

    # Run the keygen to generate images
    print("Generating images...")
    subprocess.run(["python", "keygen.py", username], check=True)
    print("Images generation OK")

    try:
        subprocess.run(["./brachiosaure", username, "img1.png", "img2.png"], check=True)
    except Exception as e:
        print("Images are not valid, trying again...")
        continue

    # It worked, submit the images
    print("Found valid images for username", username)
    resp = requests.post(URL + "login", files = {"upload1": open("img1.png", "rb"), "upload2": open("img2.png", "rb")}).text
    if "FCSC{" in resp:
        print("Got the flag:", re.search("(FCSC{.*})", resp).groups()[0])
        break
    else:
        print("Server refused the images, trying again...")



        
