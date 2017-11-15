#!/usr/bin/python
# =============================================================================

# Leave Now - Encouraging stress-free travel to your local MTA subway station
# by knowing when it's time to leave home.

# Version 1.4 15-Nov-2017 by Rob D <http://github.com/rob718/mta-leavenow>
# Based on a concept written by Anthony N <http://github.com/neoterix/nyc-mta-arrival-notify>

# == Change Log
# v1.4 15-Nov-2017: General tweaks and code cleanup.
# v1.3 13-Nov-2017: Now ignoring trains that 'appear' to arrive in the past
# v1.2 12-Nov-2017: My room mate requested that we display train arrival times
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
#import scrollphathd

# You'll also need an API key. Get yours from http://datamine.mta.info/user
api_key = 'YOUR_KEY'

# Specifiy the subway station ID to use. For example 'R31N' for "Northbound
# Atlantic Av - Barclays Ctr"
subway_station_id = 'R31N'

# How long does it take (in second) to walk to this subway station
station_travel_time = 170

# Which subway feeds should we use for this subway station? MTA feeds are
# based on subway lines and some stations have multiple lines, therefore
# you may need to specify more than one. Comma seperate these. Of course
# it only makes sense to specify lines that pass through that station.
# For more info see http://datamine.mta.info/list-of-feeds
subway_feed_ids = [16,21]

# How long should we wait before attempting to refresh the feed (in seconds)?
# Each time we make a request, we're pulling back anything from 50 to 120 kiBs
# It doesn't sound much, but with a delay of 30 seconds, for two lines (feeds),
# expect to pull around 450 MiB in a 24 hour period! On a RaspPi Zero, expect
# a turn-around of retrieving and processing data to be around 12-15 secs.
refresh_delay = 45

# In case we are unable to connect and/or process the feed, how many attemps
# before giving up (default is 30)
max_attempts = 30

# Function to handle display -this will run continuously as a seperate thread
def scrolldisplay():
    text_to_display = None
    while True:
        if text_to_display != display_message:
            # message has changed, let's update display
            text_to_display = display_message
            print ('{} mta-leavenow:{}'
                .format(time.strftime('%b %d %H:%M:%S'),text_to_display) )
            
            # third-party display specific commands here
            #scrollphathd.clear()
            #scrollphathd.set_brightness(0.1)
            #scrollphathd.write_string(text_to_display)
        else:
            # no change, so continue to show original message
            
            # third-party display specific commands here
            #scrollphathd.show()
            #scrollphathd.scroll()

            time.sleep(0.02)

# Function connects to MTA feed and gets list of trains for the given station.
def station_time_lookup(feed_id, station_id):
    global display_message

    for attempt in range((max_attempts - 1)):
        try:
            # Get the MTA's data feed for a given set of lines. For more info,
            # see http://datamine.mta.info/list-of-feeds. The format of the feed
            # is "GTFS Realtime" (based on "protocol buffers") by Google.
            # Retrieval takes around 8-9 seconds on a RaspPi Zero
            transit_feed_pb = gtfs_realtime_pb2.FeedMessage()
            response = urllib.urlopen('http://datamine.mta.info/mta_esi.php?key={}&feed_id={}'
                .format(api_key, feed_id))
            transit_feed_pb.ParseFromString(response.read())

            # Convert feed from Google's "protocol buffer" to a dictionary
            # and attempt to read FeedEntity message. Sometimes we have to
            # retry as a full dataset is not always provided by MTA. See:
            # https://developers.google.com/transit/gtfs-realtime/reference/
            # Conversion takes around 2-3 seconds on a RaspPi Zero
            transit_feed_dict = protobuf_to_dict(transit_feed_pb)
            train_data = transit_feed_dict['entity']

        except:
            if attempt <= max_attempts:
                display_message = (' ERROR getting data. Delaying for 30s. Attempt {} of {}.'
                    .format((attempt + 1), max_attempts))
                time.sleep(30)
                continue
            else:
                display_message = (' ERROR getting data. Max # of retries attempted.')
                time.sleep(10)
                raise

        break

    # Loop through the data to get train times, and line info
    arrival_list = []
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

    # Return two-dimensional list: arrival time, train name
    return arrival_list

# Original function that let's you know when it's time to leave your home/office by
# factoring in travel time.
def leavenow():
    global display_message

    # start display in a seperate thread
    display_message = (' Getting data...')
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
            for index, train in enumerate(station_trains):

                # determine next arrival time
                current_time = int(time.time())
                train_arrival = int((train[0] - current_time))

                # do not show past arrivals (e.g. a train arriving in -2 minutes)
                # or trains that you'll never make (i.e. factor in station travel time)
                if (train_arrival - station_travel_time) >= 0:

                    # calc mins remaining using train arrival time, and subway travel time
                    train1_name = str(station_trains[index][1])
                    train2_name = str(station_trains[index + 1][1])
                    train1_mins_to_leave = int(round(((
                        station_trains[index][0] - current_time - station_travel_time) / 60.0),0))
                    train2_mins_to_leave = int(round(((
                        station_trains[index + 1][0] - current_time - station_travel_time) / 60.0),0))

                    # NOTE: This section could be improved. While it works well for stations
                    # around 5-8 mins away, it might not for stations taking longer
                    if train1_mins_to_leave < 1:
                        display_message = ('     Leave NOW for ({}) or {}\' for ({}).'
                            .format(train1_name, train2_mins_to_leave, train2_name))
                        break
                    elif train1_mins_to_leave > 1:
                        display_message = ('     Leave in {}\' for ({}) or {}\' for ({}).'
                            .format(train1_mins_to_leave, train1_name,
                                train2_mins_to_leave, train2_name))
                    break
        else:
            display_message = (' No trains.')

        time.sleep(refresh_delay)

# New function (since version 1.2) that shows the times of the next two trains.
def traintime():
    global display_message

    # start display in a seperate thread
    display_message = (' Getting MTA data...')
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
            for index, train in enumerate(station_trains):

                # determine next arrival time
                current_time = int(time.time())
                train_arrival = int((train[0] - current_time))

                # do not show past arrivals (e.g. a train arriving in -2 minutes)
                # or trains that you'll never make (i.e. factor in station travel time)
                if (train_arrival - station_travel_time) >= 0:

                    # in an attempt to make this section easier to read...
                    train1_name = str(station_trains[index][1])
                    train2_name = str(station_trains[index + 1][1])
                    train1_minsaway = int(round(((
                        station_trains[index][0] - current_time) / 60.0),0))
                    train2_minsaway = int(round(((
                        station_trains[index + 1][0] - current_time) / 60.0),0))

                    display_message = ('     ({}) in {}\' then ({}) in {}\''.format(
                        train1_name, train1_minsaway,
                        train2_name, train2_minsaway))
                    break

        else:
            display_message = (' No trains.')

        time.sleep(refresh_delay)

# Uncomment either line below to switch the behaviour of the program between the
# original, "leavenow" mode (letting you know when it's time to leave your home/office)
# or "traintime" mode that simply displays the arrival times of the next two trains.
#if __name__ == '__main__': leavenow()
if __name__ == '__main__': traintime()
