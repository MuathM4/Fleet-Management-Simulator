AI Fleet Simulator
I built this to see if I could turn Euro Truck Simulator 2 into a real telematics dataset — pull live physics data straight out of the game, log it, and train a model to catch bad driving in real time.
The data
I drove 10 transport missions across ETS2, logging over 10,000 km and roughly 66,000 seconds of raw telemetry. Every second gets tagged with speed, RPM, gear, throttle/brake position, steering angle, and G-forces on all three axes (Accel_X, Accel_Y, Accel_Z).
One annoying problem early on: pausing the game (or opening a menu) kept polluting the dataset with garbage frames. I ended up writing a small detector that recognizes the pause state and stops logging automatically, otherwise the "ground truth" labels were meaningless.
The model
Random Forest, 100 estimators. Nothing exotic — it just works well on this kind of tabular sensor data.
Labels come from dynamic thresholding rather than fixed cutoffs. For example, harsh cornering is flagged based on lateral G-force relative to speed, not some hardcoded number that falls apart the moment you're going faster or slower than expected.
On a held-out 20% test split, it hits 99.22% accuracy. Breaking that down by class:
ClassPrecisionNormal Driving99%Harsh Cornering97%Speeding96%Low Fuel99%
Speeding and cornering are the weaker spots, which makes sense — those are the classes with fuzzier boundaries in real driving too.
Running it
pip install -r requirements.txt
Then start the logger while ETS2 is running — it hooks into the game's API and streams telemetry in the background. If you want to retrain the model or poke around the dataset yourself, open ai_model_training.ipynb.
