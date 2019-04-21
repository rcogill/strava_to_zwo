## Generate Zwift Workout Files from Strava Activities

This repository contains a script that will automatically generate Zwift structured workouts based on actual outdoor activities. For example, this would allow one to practice the precise efforts associated with a specific race on the indoor trainer. All that is required in this example is a rider's power data from a past race we want to mirror in our training.

Specifically, the Python script `strava_to_zwo.py` will generate a Zwift structured workout file (.zwo format) based on a provided JSON-formatted Strava sctivity file. The exact usage of this script is:

`python strava_to_zwo.py --in_file FILENAME.json --ftp FTP_VALUE`

where `FILENAME.json` is the file containing the Strava activity stream and `FTP_VALUE` is the user's Functional Threshold Power (FTP) in watts.

To access an activity stream, append `streams` to the URL of the page of the associated Strava activity. For example, if the Strava activity page is `https://www.strava.com/activities/2264175248`, the corresponding stream can be accessed at `https://www.strava.com/activities/2264175248/streams`. This JSON-formatted activity stream can then be saved directly within your browser or by cutting-and-pasting into a text editor. A sample activity stream is provided in the file `rc_fig_8.json` in this repository.

Once a .zwo file has been generated, this workout can be used within Zwift by placing this file in the `Documents/Zwift/Workouts/<<Numeric Zwift Id>>` directory associated with your Zwift installation. Detailed instructions on how to use custom structured workout files within Zwift are provided [HERE](`https://support.zwift.com/en/-sharing-importing-custom-workouts-(.zwo-files)-(cycling)-r1IlCybrQ`). 

In addition to the `strava_to_zwo.py` script, this repository contains a Jupyter notebook that elaborates on the steps required to generate the structured workout file.
