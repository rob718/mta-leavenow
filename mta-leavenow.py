#!/usr/bin/python
# =============================================================================

# Leave Now - Encouraging stress-free travel to your local MTA subway station
# by knowing when it's time to leave home.

# Version 1.2 12-Nov-2017 by Rob D <http://github.com/rob718/mta-leavenow>
# Based on a concept written by Anthony N <http://github.com/neoterix/nyc-mta-arrival-notify>

# == Change Log
# v1.2 12-Nov-2017: My roommate requested that we display train arrival times
#	instead of this program's original intent, where we tell you when it's
#	time to leave your home or office by factoring in the station travel
#	time. So here it is - uncomment either of the last two lines in this file
#	to switch program behaviour (the original, "leavenow" mode or the new
#	"traintime" mode). Also added error checking when getting the MTA feed.
#
# v1.1 04-Nov-2017: Added Scroll pHAT HD Support
# v1.0 29-Oct-2017: Initial version

# == Prerequisites
# Install Google's "gtfs-realtime-bindings" and Ben Hodgson's "protobuf-to-dict"
# libraries. Depending on your system, you can install them with something like:
#  pip install --upgrade gtfs-realtime-bindings
#  pip install --upgrade protobuf-to-dict

# == License
# This is free and unencumbered software released into the public domain.

# Anyone is free to copy, modify, publish, use, compile, sell, or
# distribute this software, either in source code form or as a compiled
# binary, for any purpose, commercial or non-commercial, and by any
# means.

# In jurisdictions that recognize copyright laws, the author or authors
# of this software dedicate any and all copyright interest in the
# software to the public domain. We make this dedication for the benefit
# of the public at large and to the detriment of our heirs and
# successors. We intend this dedication to be an overt act of
# relinquishment in perpetuity of all present and future rights to this
# software under copyright law.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

# For more information, please refer to <http://unlicense.org>
# =============================================================================
from google.transit import gtfs_realtime_pb2
from protobuf_to_dict import protobuf_to_dict
import urllib
import time
import threading

# Enable support for third-party displays like the Pimoroni scroll pHAT HD
import scrollphathd

# Specifiy the subway station ID to use. For example 'R31N' for "Northbound
# Atlantic Av - Barclays Ctr"
subway_station_id = 'R31N'

# How long does it take (in second) to walk to this subway station
station_travel_time = 220

# Which subway feeds should we use for this subway station? MTA feeds are
# based on subway lines and some stations have multiple lines, therefore
# you may need to specify more than one. Comma seperate these. Of course
# it only makes sense to specify lines that pass through that station.
# For more info see http://datamine.mta.info/list-of-feeds
subway_feed_ids = [16,21]

# You'll also need an API key. Get yours from http://datamine.mta.info/user
api_key = 'YOUR_KEY'

# Function to handle display. In this case, the Pimoroni scroll pHAT is used
def scrolldisplay():
    global display_message
    text_to_display = None
    while True:
        if text_to_display != display_message:
            # display message has changed, let's update
            text_to_display = display_message
            print 'mta-leavenow:{}'.format(text_to_display)
            scrollphathd.clear()
            scrollphathd.set_brightness(0.1)
            scrollphathd.write_string(text_to_display)
        else:
            # no change, continue to show original message
            scrollphathd.show()
            scrollphathd.scroll()
            time.sleep(0.01)

# Function connects to feed and gets list of trains for the given station.
# Returns two-dimensional list: arrival time, train name
def station_time_lookup(feed_id, station_id):
    global display_message
    arrival_list = []

    # number of attempts to connect to MTA feed after failure
    tries = 8
    for i in range(tries):
        try:
            # Get the MTA's data feed for a given set of lines. For more info,
            # see http://datamine.mta.info/list-of-feeds. The format of the feed
            # is "GTFS Realtime" (based on "protocol buffers") by Google.
            feed = gtfs_realtime_pb2.FeedMessage()
            response = urllib.urlopen('http://datamine.mta.info/mta_esi.php?key={}&feed_id={}'
                .format(api_key,feed_id))
            feed.ParseFromString(response.read())
            
            # Convert the feed from Google's "protocol buffer" to a dictionary
            subway_feed = protobuf_to_dict(feed)
            train_data = subway_feed['entity']
        except:
            if i < tries - 1:
                display_message = ' ERROR connecting to MTA feed. Retrying.'
                time.sleep(2)
                continue
            else:
                display_message = '#fail'
                time.sleep(2)
                raise
        break

    # Loop through the data to get train times, and line info
    for trains in train_data:
        if trains.get('trip_update', False) != False:
            train_trips = trains['trip_update']
            station_times = train_trips['stop_time_update']
            train_trip_details = train_trips['trip']
            train_name = train_trip_details['route_id']

            # Filter out data not pertaining to the given station
            # (and direction) and get train arrivals, and train names            
            for arrivals in station_times:
                if arrivals.get('stop_id', False) == station_id:
                    train_time_data = arrivals['arrival']
                    train_time = train_time_data['time']
                    if train_time != None:
                        arrival_list.append([train_time,train_name])
                        #print 'debug:',train_time,train_name

    return arrival_list

# Original function that let's you know when it's time to leave your home/office by
# factoring in travel time.
def leavenow():
    # declare global variables for display message, and set initial message
    global display_message
    global display_message_lastupdate
    display_message = ' Getting data...'

    # start display in a seperate thread
    display = threading.Thread(target=scrolldisplay)
    display.daemon = True
    display.start()

    # loop indefinitely, pausing for a set time
    while True:

        # get list of trains for given station, and sort based on arrival time
        station_trains = []
        for subway_feed_id in subway_feed_ids:
            station_trains.extend(station_time_lookup(subway_feed_id,subway_station_id))
            station_trains.sort()

        if station_trains:
            for next_train in station_trains:

                # calc mins remaining using train arrival time, and subway travel time
                current_time = int(time.time())
                arrival_mins = int((next_train[0] - current_time))
                mins_to_go = int(round(((arrival_mins-station_travel_time)/60.0),0))

                # NOTE: This section could be improved. While it works well for stations
                # around 5-8 mins away, it might not for stations taking longer
                train_name = str(next_train[1])
                if mins_to_go == 1:
                    display_message = ('     Leave NOW to for ({})'.format(train_name))
                    break
                elif mins_to_go > 1:
                    display_message = ('     Leave in {}\' for ({})'.format(mins_to_go,train_name))
                break
        else:
            display_message = (' No trains.')

        time.sleep(5)

# New function (since version 1.2) that shows the times of the next two trains.
def nexttrain():
    # declare global variables for display message, and set initial message
    global display_message
    display_message = ' Getting data...'
                
    # start display in a seperate thread
    display = threading.Thread(target=scrolldisplay)
    display.daemon = True
    display.start()
                
    while True:
        station_trains = []
        for subway_feed_id in subway_feed_ids:
            station_trains.extend(station_time_lookup(subway_feed_id,subway_station_id))
            station_trains.sort()
        if station_trains:
            current_time = int(time.time())
            display_message = '     ({}) in {}\' then ({}) in {}\''.format(
                str(station_trains[0][1]),
                int(round(((station_trains[0][0] - current_time) / 60.0),0)),
                str(station_trains[1][1]),
                int(round(((station_trains[1][0] - current_time) / 60.0),0))
                )
        else:
            display_message = (' No trains.')

        #print 'debug:',display_message
        time.sleep(5)

# Uncomment either line below to switch the behaviour of the program between the
# original, "leavenow" mode (letting you know when it's time to leave your home/office)
# or "traintime" mode that simply displays the arrival times of the next two trains.
if __name__ == '__main__': leavenow()
#if __name__ == '__main__': nexttrain()
