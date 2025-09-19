from dotenv import load_dotenv
import os
import discord
import pandas as pd
from discord.ext import commands
import requests
from google.transit import gtfs_realtime_pb2
from datetime import datetime, timedelta

class translink(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        # Load environment variables from the .env file
        load_dotenv()

        # Get the TransLink API Key from the .env file
        self.api_key = os.getenv('TRANSLINK_API_KEY')  # Fetch the API key securely

        # Check if the API key is loaded properly
        if not self.api_key:
            raise ValueError("API key not found. Please set the TRANSLINK_API_KEY environment variable.")
        
        # Load the GTFS data files
        self.stops = pd.read_csv('./data/stops.txt')
        self.stop_times = pd.read_csv('./data/stop_times.txt')
        self.trips = pd.read_csv('./data/trips.txt')
        self.routes = pd.read_csv('./data/routes.txt')

        # Strip leading/trailing spaces from column names
        self.stops.columns = self.stops.columns.str.strip()
        self.stop_times.columns = self.stop_times.columns.str.strip()
        self.trips.columns = self.trips.columns.str.strip()
        self.routes.columns = self.routes.columns.str.strip()

        # Convert stop_code to integer and then to string to match format in file
        self.stops['stop_code'] = self.stops['stop_code'].astype('Int64').astype(str)

    def get_gtfs_realtime_feed(self):
        url = f'https://gtfsapi.translink.ca/v3/gtfsrealtime?apikey={self.api_key}'
        response = requests.get(url)
        if response.status_code == 200:
            feed = gtfs_realtime_pb2.FeedMessage()
            feed.ParseFromString(response.content)
            return feed
        else:
            print(f"Error: Unable to fetch GTFS Realtime feed, status code: {response.status_code}")
            return None

    def get_upcoming_buses(self, feed, stop_id):
        upcoming_buses = []
        now = datetime.now()
        one_hour_from_now = now + timedelta(hours=1)

        for entity in feed.entity:
            if entity.HasField('trip_update'):
                trip_update = entity.trip_update
                for stop_time_update in trip_update.stop_time_update:
                    if stop_time_update.stop_id == str(stop_id):
                        arrival_time = datetime.fromtimestamp(stop_time_update.arrival.time)

                        if now <= arrival_time <= one_hour_from_now:
                            route_id = trip_update.trip.route_id
                            stop_sequence = stop_time_update.stop_sequence
                            upcoming_buses.append((route_id, arrival_time, stop_sequence))

        upcoming_buses.sort(key=lambda x: x[1])
        return upcoming_buses

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} is online!")

    @commands.command(name='routes')
    async def get_routes(self, ctx, stop_code: str):
        stop_id_row = self.stops[self.stops['stop_code'] == stop_code]

        if len(stop_id_row) == 0:
            await ctx.send(f"No stop found for stop_code {stop_code}")
            return

        stop_id = stop_id_row['stop_id'].values[0]

        # Fetch GTFS Realtime feed and upcoming buses
        feed = self.get_gtfs_realtime_feed()
        upcoming_buses = self.get_upcoming_buses(feed, stop_id) if feed else []

        # Find trip_ids that include this stop_id
        trip_ids = self.stop_times[self.stop_times['stop_id'] == stop_id]['trip_id'].unique()

        # Find route_ids that include these trip_ids
        route_ids = self.trips[self.trips['trip_id'].isin(trip_ids)]['route_id'].unique()

        # Get route details
        routes_info = self.routes[self.routes['route_id'].isin(route_ids)]

        if routes_info.empty:
            await ctx.send(f"No routes found for stop_code {stop_code}")
        else:
            embed = discord.Embed(title=f"Routes at stop {stop_code}", color=discord.Color.blue())

            for _, route in routes_info.iterrows():
                route_id = route['route_id']
                route_name = route['route_long_name']
                route_short_name = route['route_short_name']

                # Prepare the message string for this route
                route_info = f"**{route_short_name}: {route_name}**\nUpcoming Departures:\n"
                
                # Check for upcoming buses for this route
                buses_for_route = [bus for bus in upcoming_buses if bus[0] == route_id]

                if buses_for_route:
                    for bus in buses_for_route:
                        arrival_time = bus[1].strftime('%H:%M:%S')
                        route_info += f"{arrival_time}\n"
                else:
                    route_info += "No buses within the next hour\n"

                # Add the route information as a field in the embed
                embed.add_field(name="\u200b", value=route_info, inline=False)

            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(translink(bot))
