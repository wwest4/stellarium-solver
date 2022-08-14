# Plate Solving for Manual Mounts

These are the notes from my initial investigation.

## Problem
Without a goto-capable mount, I aim my tube + camera by hand. Even with a wide-field scope, it can be hard to tell where exactly the scope is pointed. Basically my method is to image at high gain for 15+ seconds, look at the star field, and visually scan for the same star patterns in Stellarium, since I know roughly where I am. I’ve survived a year doing this, but it’s a problem for two reasons:

I am building a scope which I will use for smaller FOV operations, and I still may not have goto capability
It is time-consuming to visually/manually plate solve, which I could spend collecting data a not getting bitten by mosquitos

I’ve tried speeding this up by feeding preview images to astrometry.net’s web service, but this is tedious and doesn’t save much time.  It occurred to me that Stellarium probably has some ability to set its view programmatically, and I could probably automate the process of sending preview images to a real plate solver and then use that to set the Stellarium view.

Confirmed: the programmatic method does exist by enabling the Remote Control Plugin and using the web API: https://stellarium.org/doc/head/remoteControlApi.htm, example:

```
curl -X POST http://localhost:8090/api/main/view -d ‘j2000=[1,1,0]’
curl -X POST  http://localhost:8090/api/main/fov -d ‘fov=6’
```

… this will also accept altaz and jNow coords. FOV controls the zoom… 6 is a good rule of thumb for scanning around further. These changes can also be made via the scripting engine, which has access to public members of core and plugin APIs (this turns out to be the better option short of writing a new plugin, because of the access to the whole API).

Astrometry.net has an offline plate solver.. My control laptop is a linux box so it apparently requires building from source, which could be a pain in the ass, but nice for being able to plate solve in remote sites where internet is not available. Can start with the online solver though.

Should be possible to write some glue code that scans for new preview images in a certain location, solves them, converts the resulting coordinates to input for Stellarium, and then posting to the Stellarium API to set the view, fov, rotation, and more. This should reduce the workflow to one step (clicking one or two buttons in the capture software). Cognitive load is reduced to almost nothing. A local plate solver with indices tuned to the scope’s field of view should further reduce the time to solve.

## Building & installing astrometry.net offline solver
* Grab the tarball https://astrometry.net/downloads/
* Extract
* Install any missing deps; for my ubuntu-based distro this was: `gcc, zlib1g-dev, libbz2-dev, libcfitsio-dev, pkg-config, python3-fitsio` (YMMV)
* Install optional deps: `libcairo2-dev, libjpeg-dev, python3-numpy, swig, python3-dev`
* Run make; ensure the build succeeds.
* Run sudo make install; ensure no fatal errors.

## Install indices
Get pre-cooked index files from: <http://data.astrometry.net/4200>_ (these are built from the 2MASS catalog).
Or, for wide-angle images, <http://data.astrometry.net/4100>_ (these are built from the Tycho-2 catalog).
The files are named like index-42XX.fits or index-42XX-YY.fits. XX is the “scale”, YY is the “healpix” number. These are called the “4200-series” index files.
Each index file contains a large number of “skymarks” (landmarks for the sky) that allow our solver to identify your images. The skymarks contained in each index file have sizes (diameters) within a narrow range. You probably want to download index files whose quads are, say, 10% to 100% of the sizes of the images you want to solve.
For example, let’s say you have some 1-degree square images. You should grab index files that contain skymarks of size 0.1 to 1 degree, or 6 to 60 arcminutes. 
https://github.com/dstndstn/astrometry.net/blob/master/util/hp.png https://github.com/dstndstn/astrometry.net/blob/master/util/hp2.png


…my widefield rig has a FOV of about 4deg4.36’x3deg3.30’ according to Stellarium’s Oculars plugin, so according to the instructions, I should grab index files that contain skymarks of 0.4 - 4 degree, or 24 - 240 arcminutes: 
    …this means grabbing the highlighted files. For the above selection:

```
for x in $(seq -w 2 7); do for y in $(seq -w 0 47); do wget http://data.astrometry.net/4200/index-420$x-$y.fits; done; done
for x in $(seq -w 8 13); do http://data.astrometry.net/4200/index-420$x.fits; done
```

Run this in the top level of the build directory and then do a `sudo make install-indexes`.

## Running the solver

```
/usr/local/astrometry/bin/solve-field --guess-scale image.fit
```

This takes a long time on a chromebook. Optimization by rough area in the sky? YES:

```$ solve-field --ra, --dec, --radius```

…the current Stellarium view and fov can be obtained from the remote control API to feed these parameters.

The coordinates, when solved, end up in `image.wcs`... they can be extracted with the included wcsinfo utility:

```
/usr/local/astrometry/bin/wcs-info image.wcs
```


## Enable the remote control service on Stellarium
* Open Stellarium
* Open the Configuration Window
* Go to the Plugins tab
* Scroll to “Remote Control”
* Check on the “Load at Startup” option
* Restart Stellarium
* Return to the Configuration Window/Plugins tab/Remote Control plugin pane
* Click the “Configure” button
* Check on the “Server Enabled” and “Enable automatically on Startup” options
* Select port, auth, CORS and other options as you need
* Click Save settings

Test that port to be sure the service is up and available. 
```curl http://localhost:port/api/main/status | jq .```

Tie this together: write interstitial python daemon that uses templates to generate ssc code and invoke it through the /api/scripts/direct endpoint.
The script should be able to:
* Set RA/Dec view
* Zoom to the FOV
* Orient the Oculars CCD frame to the orientation of the real camera
