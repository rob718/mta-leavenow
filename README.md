# mta-leavenow
A python script that let’s you know when it’s time to leave home to make the next subway train. The script basically reads the NYC MTA data feed to determine the next arrival train for a given station. It then let’s you know (in minutes) when to leave your home or office based on the train arrival time and how long it takes to walk to the station in question.
This script could easily be modified to work with other transport systems utilizing Google’s GTFS Reatime format.
https://developers.google.com/transit/gtfs-realtime/

***Update 12-Nov-2017***: My room mate requested that we display train arrival times instead of this program's original intent, where we tell you when it's time to leave your home or office by factoring in the station travel time. So here it is - uncomment either of the last two lines in this file to switch program behaviour (the original, "leavenow" mode or the new "traintime" mode). Also added error checking when getting the MTA feed.

Note that the script currently outputs to both the console and a [Scroll pHAT](https://shop.pimoroni.com/products/scroll-phat-hd). It should be simple enough to change this for your needs e.g. a [Sense HAT](https://www.raspberrypi.org/products/sense-hat/).

# Prerequisites
The following packages are needed:  Google's [gtfs-realtime-bindings](https://github.com/google/gtfs-realtime-bindings) and Ben Hodgson's [protobuf-to-dict](https://github.com/kaporzhu/protobuf-to-dict). Depending on your system, you can install them with something like:
```
pip install --upgrade gtfs-realtime-bindings
pip install --upgrade protobuf-to-dict
```

You’ll also need an API key that you can register for here: http://datamine.mta.info/user/register and any libraries for the display you're using - in my case a [Scroll pHAT](https://shop.pimoroni.com/products/scroll-phat-hd).

Finally you’ll need to know the IDs for both the train lines, and the subway station that you want to monitor. The script supports multiple feed IDs in case multiple lines cover a the station in question. For more information see: http://datamine.mta.info/list-of-feeds

# Installation and Configuration

With git installed, you can do the following to get it on your system. Copy and paste also works.
```
git clone https://github.com/rob718/mta-leavenow.git
```

**API Key, station ID, and line ID** - You’ll then need to edit the script to update it with your own API key and IDs for both the lines and station you want to monitor. See the prerequisites section above.

**Which mode?** - Don't forget to uncomment either of the last two lines of the script to switch the behaviour of the program, the original, "leavenow" mode letting you know when it's time to leave your home/office, or the new "traintime" mode that simply displays the arrival times of the next two trains.

# Execution
I typically run the script under screen, and append an ampersand to the end so that it runs the script in the background. I then press ***CTRL-A***, then ***D*** to detach the current screen and logout.
```
python ./mta-leavenow.py &
```
If I ever want to return to stop the script, I simply enter ***screen -r*** to resume and then ***fg*** to bring the script to the foreground, before pressing ***CTRL-C*** to stop it. For more information about screen, see: https://www.gnu.org/software/screen/manual/screen.html.

I wouldn't recommend this method for more permanent fixtures as you'll probably need something that will autostart on boot.

# Background
I don’t know about you, but I always run down those subway steps thinking I’ll miss the train if I don’t. One day I’m gunna fall. Seriously. How about a Raspberry Pi Zero connected to a set of LEDs counting down to the next subway train? Better yet, how about a scrolling display telling you when it’s time to leave home? Yes, that’s what I thought! I built this script to provide me (and maybe you!) stress-free travel to the local MTA station.

# Acknowledgments
Based on a concept written by Anthony N http://github.com/neoterix/nyc-mta-arrival-notify
