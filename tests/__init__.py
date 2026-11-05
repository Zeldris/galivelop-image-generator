import os

# No test starts the local service by accident (F3.5); the ones that want it set GIMG_AUTOSTART=1 themselves.
os.environ["GIMG_AUTOSTART"] = "0"
