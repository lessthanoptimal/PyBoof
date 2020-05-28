#!/usr/bin/env python3

import os
import signal

pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]

for pid in pids:
    try:
        text = open(os.path.join('/proc', pid, 'cmdline'), 'rb').read()
        if 'PyBoof' in str(text):
            os.kill(int(pid), signal.SIGTERM)
            print("Killed "+pid)
    except IOError: # proc has already terminated
        continue

print("Done")