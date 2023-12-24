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
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options

bot = commands.Bot()
TESTING_GUILD_ID = 1166111304617041920

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

# Configure Chrome options for headless mode
options = Options()
options.add_argument("--headless")  # Explicitly add headless argument
options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration
options.add_argument("--no-sandbox")  # Bypass OS security model
options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems

driver = webdriver.Chrome(options=options) 

def return_classes(email):
    driver = webdriver.Chrome(options=options) 
    driver.get(f"https://www.dickinson.edu/site/custom_scripts/dc_faculty_profile_index.php?fac={email}")

    # Extract Education Details
    education_details = []
    try:
        education_section = driver.find_element(By.XPATH, "//h3[contains(text(), 'Education')]/following-sibling::ul")
        for item in education_section.find_elements(By.TAG_NAME, "li"):
            education_details.append(item.text)
    except NoSuchElementException:
        print("No Education section found.")

    # Click on the 'Course Info' tab
    try:
        course_info_tab = driver.find_element(By.XPATH, "//a[@href='#courses']")
        course_info_tab.click()
    except NoSuchElementException:
        print("Course Info tab not found.")

    # Function to extract course names
    def extract_courses(xpath):
        course_elements = driver.find_elements(By.XPATH, xpath)
        unique_courses = set()
        for course in course_elements:
            course_name = course.text.split('\n')[0]
            unique_courses.add(course_name)
        return sorted(list(unique_courses), key=lambda x: int(x.split(' ')[1]))

    # Extract Course Names for Fall and Spring
    fall_courses = extract_courses('//h3[contains(text(), "Fall")]/following-sibling::p')
    spring_courses = extract_courses('//h3[contains(text(), "Spring")]/following-sibling::p')
    driver.quit()

    return education_details, fall_courses, spring_courses

@bot.event
async def on_ready():
    print(f'Login as {bot.user} successful!')
@bot.slash_command(description="Finds People using First and Last Name OR Email", guild_ids=[TESTING_GUILD_ID])
async def search(interaction: nextcord.Interaction, first_name: str = None, last_name: str = None, email: str = None):
    await interaction.response.defer(ephemeral=True)
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
        education, fall_courses, spring_courses = return_classes(result['EMAIL'])
        embed.add_field(name="Education", value='\n'.join(education), inline=False)
        embed.add_field(name="Fall Courses", value='\n'.join(fall_courses), inline=False)
        embed.add_field(name="Spring Courses", value='\n'.join(spring_courses), inline=False)
        driver.quit()
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
    await interaction.followup.send(embed=embed,ephemeral=True)
bot.run("banana bread :D")
