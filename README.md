# Galeria

Try to extract paths of people walking from my video taken from Galeria
in Berlin

# Install

    virtualenv env
    source ./env/bin/activate
    pip install -r requirements.txt

# Run (with basic Lucas-Kanade Optical Flow)

    source ./env/bin/activate
    python main_lk.py in/20649264_494002477619041_4614638744018878464_n.mp4 out/output.mp4

# Run (with LK, but trying to identify new features)

    source ./env/bin/activate
    python main_lk_restart.py in/20649264_494002477619041_4614638744018878464_n.mp4 out/output_restart.mp4

