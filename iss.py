#!/usr/bin/env python
'''The ISS program Tracks the ISS and astronauts in space in real time
    also provides gui for visual tracking of the ISS and specific times
    the ISS will pass over specific destinations supplied by the user.'''

__author__ = '''Jordan Kubista with help from request docs, python turtle
                docs and google to rethink my lat and lon knowledge'''

import turtle
import requests
import time
import sys
import argparse


# Gets the astronauts
def get_astronauts():
    '''Submits a get request to print the list of astronauts full names,
       spacecraft they're onboard and total astronauts in space'''

    astro_specs = requests.get('http://api.open-notify.org/astros.json')

    if astro_specs.status_code == 200:
        astro_dict = astro_specs.json()
        print(f'''\nThere are {astro_dict.get("number")} astronauts in\
 space right now.\n''')
        astronauts = astro_dict.get('people')
        for name in astronauts:
            astronaut = name.get('name')
            craft = name.get('craft')
            print(f'--{astronaut}\n---- aboard the {craft}\n')
    else:
        print(f'We received a - {astro_specs.status_code} - error while\
 processing your request, check your URL and try again.')


# Gets the ISS current Coordinates
def current_coords():
    '''Submits a get request to receive the iss lat/lon and timestamp'''

    iss_locate = requests.get('http://api.open-notify.org/iss-now.json')

    if iss_locate.status_code == 200:
        iss = iss_locate.json()
        iss_time = iss.get('timestamp')
        human_time = time.ctime(iss_time)
        position = iss.get('iss_position')
        lat = position.get('latitude')
        lon = position.get('longitude')
    else:
        print(f'We received a - {iss_locate.status_code} - error while\
 processing your request, check your URL and try again.')
    coords_time = (lon, lat, human_time)

    return coords_time


# Gets the time for Indianas pass over
def over_indi():

    get_pass = requests.get('http://api.open-notify.org/iss-pass.json?\
lat=39.768402&lon=-86.158066')
    indi_pass = get_pass.json()
    indi_pass_stats = indi_pass.get('response')
    pass_time = indi_pass_stats[0]
    indi_human_time = time.ctime(pass_time.get('risetime'))

    return(indi_human_time)


# Map creator and controller
def real_time_map(user_time=None):
    '''Makes use of the turtle library to create a map and location
        for the ISS and for Indianapolis, Indiana. Updates every 10
        seconds'''

    indi_pass = over_indi()
    iss_stats = current_coords()
    lat = float(iss_stats[0])
    lon = float(iss_stats[1])

    turtle.setup(width=720, height=360, startx=None, starty=None)
    turtle.mode(mode='world')
    turtle.setworldcoordinates(-180, -90, 180, 90)
    turtle.title(f'ISS Space Station Tracking System -- {iss_stats[2]}')
    turtle.bgpic('map.gif')
    turtle.addshape('iss2.gif', shape=None)
    turtle.addshape('yellow-dot.gif', shape=None)
    turtle.addshape('orange-dot.gif', shape=None)

    text = turtle.Turtle()
    text.color('yellow')
    text.penup()
    text.hideturtle()
    text.goto(-86.158066, 41.768402)
    text.write(f'Next pass for\nIndianapolis, Indiana\n{indi_pass}',
               move=False, font=("Arial", 10, 'underline'))

    indi = turtle.Turtle()
    indi.shape('yellow-dot.gif')
    indi.penup()
    indi.goto(-86.158066, 39.768402)

    iss = turtle.Turtle()
    iss.penup()
    iss.shape('iss2.gif')
    iss.goto(lat, lon)

    if user_time is not None:
        text.clear()
        indi.hideturtle()
        u_text = turtle.Turtle()
        u_text.color('orange')
        u_text.penup()
        u_text.hideturtle()
        u_text.goto(user_time[2], user_time[1] + 2)
        u_text.write(f'''Here is when the ISS will pass over your spot
 {user_time[0]}''', move=False, font=("Arial", 10, 'underline'))

        user = turtle.Turtle()
        user.shape('orange-dot.gif')
        user.penup()
        user.goto(user_time[2], user_time[1])

    def update_map():
        '''Continiously calls itself every 10 seconds to update location
            and time, until the program is closed.'''
        iss_stats = current_coords()
        turtle.title(f'ISS Space Station Tracking Map -- {iss_stats[2]}')
        lat = float(iss_stats[0])
        lon = float(iss_stats[1])
        iss.pencolor('purple')
        iss.pensize(3)
        iss.pendown()
        iss.goto(lat, lon)
        turtle.ontimer(update_map, 10000)

    update_map()
    turtle.Screen().exitonclick()


# Takes users choice and gets lat,lon and ISS pass Info, left my key in there
# to make things easier (positionstack.com)
def user_location(dest):
    '''Takes the user supplied destination and plots it on the
        map with the next time the ISS will pass over it'''

# Gets the users lat and lon from provided information on command line.
    get_user_coords = requests.get(f'http://api.positionstack.com/v1/forward\
?access_key=ccc6d7977313ae369933d181542eafc4&query={dest}&limit=1')

    if get_user_coords.status_code == 200:
        user_coords = get_user_coords.json()
        user_data = user_coords.get('data')
        if len(user_data) > 0:
            user_data_list = user_data[0]
            user_lat = user_data_list.get('latitude')
            user_lon = user_data_list.get('longitude')
        else:
            print(f'''We did not recieve any data back on "{dest}" please check\
 it and try again.''')
            return
    else:
        print(f'We received a - {get_user_coords.status_code} - error while\
 processing your request, check your URL and try again.')
        return
# Gets the next time the ISS will pass over the user specified location.
    get_pass = requests.get(f'http://api.open-notify.org/iss-pass.json?\
lat={user_lat}&lon={user_lon}')
    user_pass = get_pass.json()
    user_pass_stats = user_pass.get('response')
    pass_time = user_pass_stats[0]
    user_human_time = time.ctime(pass_time.get('risetime'))

    return (user_human_time, user_lat, user_lon)


def create_parser():
    parser = argparse.ArgumentParser(description='''Choose to
        get astronaut information, or
        pull up a world map to see the real time location of the
        ISS''')
    parser.add_argument('-a', '--astronauts', help='''returns the
                        astronauts full name and the craft they
                        are on.''', action='store_true')
    parser.add_argument('-r', '--rtmap', help='''returns a real time
                        map view of the ISS location.''',
                        action='store_true')
    parser.add_argument('location', help='''returns -a and -r
                        along with a user chosen location of when the
                        ISS will pass over it again. Enter location name
                        or address, wrap it in quotes if you're using
                        spaces.''', nargs='?', default='')
    return parser


def main(args):
    '''Iniates the iss program as directed by the command line.'''
    parser = create_parser()
    ns = parser.parse_args(args)

    if not ns:
        parser.print_usage()
        print(ns)
        sys.exit(1)

    astronaut = ns.astronauts
    rtmap = ns.rtmap
    user_dest = ns.location

    if len(args) == 0:
        get_astronauts()
        real_time_map()
    elif user_dest:
        get_astronauts()
        user_time = user_location(args[0])
        real_time_map(user_time)
    elif astronaut:
        get_astronauts()
    elif rtmap:
        real_time_map()


if __name__ == '__main__':
    main(sys.argv[1:])
