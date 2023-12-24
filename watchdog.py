import os
import nextcord
import discord
import requests
import json
import re
import sys
import asyncio
from nextcord.ext import commands
from nextcord import Game, Client
bot = commands.Bot()
TESTING_GUILD_ID = ID
bot = Client(activity=Game(name="Blitz on Chess.com"))
#Special Info
special_email = "chermsit@dickinson.edu"
special_pic_url = "https://cdn.discordapp.com/attachments/778063171654910004/1188350065073475604/1676775800729.jpg?ex=659a343d&is=6587bf3d&hm=32cf2ba6cd1ef36c3ea6837e1625ec4f6a4b32a01c186468df96423db0ddae3e&"
f = requests.get('https://www2.dickinson.edu/lis/angularJS_services/directory_open/data.cfc?method=f_getAllPeople').json()
def find_record(first_name=None, last_name=None, email=None):
    for record in f:
        if email:
            email_domain = email.split('@')[-1] if '@' in email else ''
            if record['EMAIL'] == email.split('@')[0] and email_domain == 'dickinson.edu':
                return record
        elif first_name and last_name:
            if record['FIRSTNAME'].lower() == first_name.lower() and record['LASTNAME'].lower() == last_name.lower():
                return record
    return "No matching record found."
@bot.event
async def on_ready():
    print(f'Login as {bot.user} successful!')
@bot.slash_command(description="Finds People using First and Last Name OR Email", guild_ids=[TESTING_GUILD_ID])
async def search(interaction: nextcord.Interaction, first_name: str = None, last_name: str = None, email: str = None):
    result = find_record(first_name=first_name, last_name=last_name, email=email)
    embed = discord.Embed(title="WatchDog Search Results:", color=0x00ff00)
    embed.set_author(name="WatchDog", icon_url="https://cdn.discordapp.com/attachments/778063171654910004/1188341420201889923/Untitled.jpg?ex=659a2c30&is=6587b730&hm=7e2d7490c69fa934292cb731b75282f6d60610e136d1fada18e04b981c947fde&")
    name = f"{result['FIRSTNAME']} {result['LASTNAME']}"
    embed.add_field(name="Name: ", value=name, inline=False)
    if result['STATUS'] == 'STU' and result['TITLE']:
        embed.add_field(name="Role", value=result['TITLE'], inline=False)
    else:
        # Convert STATUS codes to full words
        status_full = {"STU": "Student", "FAC": "Faculty", "STA": "Staff"}
        status_word = status_full.get(result['STATUS'], "Unknown")
        embed.add_field(name="Status", value=status_word, inline=False)
    if result['STATUS'] == 'STU':
        embed.add_field(name="Graduating Class", value=result['CLASS'], inline=False)
        embed.add_field(name="ID", value=result['ID'], inline=False)
    if result['EMAIL'] + '@dickinson.edu' == special_email:
        embed.set_image(url=special_pic_url)
    elif result['STATUS'] == 'FAC':
        profile_pic_url = f"https://www.dickinson.edu/images/faculty/large/{result['EMAIL']}.jpg"
        embed.set_image(url=profile_pic_url)
        faculty_profile_url = f"https://www.dickinson.edu/site/custom_scripts/dc_faculty_profile_index.php?fac={result['EMAIL']}"
        title_link = f"[{result['TITLE']}]({faculty_profile_url})"
        if result['TITLE']:
            embed.add_field(name="Title", value=title_link, inline=False)
        if result['DEPT1']:
            embed.add_field(name="Department", value=result['DEPT1'], inline=False)
        if result['BUILDING']:
            embed.add_field(name="Building", value=result['BUILDING'], inline=False)
        if result['ROOM']:
            embed.add_field(name="Room", value=result['ROOM'], inline=False)
    elif result['STATUS'] == 'STA':
        if result['TITLE']:
            embed.add_field(name="Title", value=result['TITLE'], inline=False)
        if result['DEPT1']:
            embed.add_field(name="Department", value=result['DEPT1'], inline=False)
        if result['BUILDING']:
            embed.add_field(name="Building", value=result['BUILDING'], inline=False)
    if result['PHONE']:
        embed.add_field(name="Phone Number", value=result['PHONE'], inline=False)
    embed.add_field(name="Email", value=f"{result['EMAIL']}@dickinson.edu", inline=False)
    embed.set_footer(text="Created by Ty Chermsirivatana '27")
    await interaction.send(embed=embed)
bot.run("banana bread :D")
