import subprocess


server = subprocess.Popen(["python", "run_server.py"])
bot = subprocess.Popen(["python", "run_bot.py"])
