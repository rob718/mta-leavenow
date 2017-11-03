# mta-leavenow
A python script that let’s you know when it’s time to leave home to make the next subway train. The script basically reads the NYC MTA data feed to determine the next arrival train for a given station. It then let’s you know (in minutes) when to leave your home or office based on the train arrival time and how long it takes to walk to the station in question.
This script could easily be modified to work with other transport systems utilizing Google’s GTFS Reatime format.
https://developers.google.com/transit/gtfs-realtime/

Note that the script just outputs to the console. You’ll need to modify it to output to a scrolling display like a [Sense HAT](https://www.raspberrypi.org/products/sense-hat/), [Scroll pHAT](https://shop.pimoroni.com/products/scroll-phat-hd) or something similar.

# Prerequisites
The following packages are needed:  Google's [gtfs-realtime-bindings](https://github.com/google/gtfs-realtime-bindings) and Ben Hodgson's [protobuf-to-dict](https://github.com/kaporzhu/protobuf-to-dict). Depending on your system, you can install them with something like:
```
pip install --upgrade gtfs-realtime-bindings
pip install --upgrade protobuf-to-dict
```

You’ll also need an API key that you can register for here: http://datamine.mta.info/user/register

Finally you’ll need to know the IDs for both the train lines, and the subway station that you want to monitor. The script supports multiple feed IDs  in case multiple lines cover a the station in question. For more information see: http://datamine.mta.info/list-of-feeds

# Installation and Configuration

With git installed, you can do the following to get it on your system. Copy and paste also works.
```
git clone https://github.com/rob718/mta-leavenow.git
```

You’ll then need to edit the script to update it with your own API key and IDs for both the lines and station you want to monitor. See the prerequisites section above.

# Execution
I typically run the script under screen, and append an ampersand to the end so that it runs the script in the background. I then press ***CTRL-A***, then ***D*** to detach the current screen and logout.
```
python ./mta-leavenow.py &
```
If I ever want to return to stop the script, I simply enter ***screen -r*** to resume and then ***fg*** to bring the script to the foreground, before pressing ***CTRL-C*** to stop it. For more information about screen, see: https://www.gnu.org/software/screen/manual/screen.html.

I wouldn't recommend this method for more permanent fixtures as you'll probably need something that will autostart on boot.

# Issues
The script bombs out if it’s unable to retrieve an MTA data feed. This seems to happen every now and again and at some point I’ll add some error capturing to at least get it to try again.

# Background
I don’t know about you, but I always run down those subway steps thinking I’ll miss the train if I don’t. One day I’m gunna fall. Seriously. How about a Raspberry Pi Zero connected to a set of LEDs counting down to the next subway train? Better yet, how about a scrolling display telling you when it’s time to leave home? Yes, that’s what I thought! I built this script to provide me (and maybe you!) stress-free travel to the local MTA station.

# Acknowledgments
Based on a concept written by Anthony N http://github.com/neoterix/nyc-mta-arrival-notify
