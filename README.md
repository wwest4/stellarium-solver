# stellarium-solver
a plate solving adapter for stellarium

Monitors for new images, plate-solves them locally, and then adjusts Stellarium+Oculars to show the latest image's location on the sky.

Very rough but basically works.

# Dependencies
- Stellarium w/ Oculars + Remote Control plugins configured + enabled
- UNIX-like OS
- astrometry.net installed locally, with suitable indexes (see their docs)
- Python >=3.6
- ASIStudio, or just drop `Preview-*.fit` files in ~/ASIImg/

# Build/Run

Install all dependencies, then:
```
python3 -m venv ./venv
source ./venv/bin/activate
pip install -r requirements.txt
nohup python solve.py &
```

If things are set up correctly, new FITS images dropped into ~/ASIImg will be plate-solved and
Stellarium's view will be moved and zoomed to the area of the image and the Oculars reticle will 
be rotated to match the image orientation.
