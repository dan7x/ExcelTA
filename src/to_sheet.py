import os
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime
from shutil import copyfile
from src.sheetwriter import course_writer
from src.class_course import Course

TA_URL = "https://ta.yrdsb.ca/yrdsb/index.php"

def write_html(login_data, out):
    session = requests.session()
    response = session.post(TA_URL, data=login_data)

    if test_conn(response):
        html_data = response.text
        html_writer(login_data['username'], out, html_data, session)

def html_writer(std_num, out, html_data, session):

    soup = BeautifulSoup(html_data, 'html.parser')
    font_list = soup.find_all('font')
    for item in font_list:
        if "Invalid Login" in str(item.text):
            print("Bad login!")
            return

    output_folder_path = dir_maker(out)
    output_subfolder = '\\' + std_num + ' TA SNAPSHOT - Generated '
    dateformat = datetime.now().strftime("%c")
    output_subfolder += dateformat

    out_path = output_folder_path + output_subfolder.replace(":", "-")
    print("Creating output folder...")
    Path(out_path).mkdir(parents=True, exist_ok=True)
    print("Output folder created! Path: " + out_path)

    c_div = soup.find('body').find("div", recursive=False)
    hrs = c_div.find_all("hr")

    c_div.find_all("div", recursive=False)[2].decompose()

    for h in hrs:
        h.decompose()

    for p in c_div.find_all('p'):
        p.decompose()

    divs_1 = soup.find_all("div", {"class": "yellow_message"})
    divs_2 = soup.find_all("div", {"class": "blue_border_message"})
    divs = divs_1 + divs_2

    UNAVAILABLE_CONST = "Please see teacher for current status regarding achievement in the course"

    filename = out_path + "\\index.html"
    out_subdir = out_path + '\\courses'
    Path(out_subdir).mkdir(parents=True, exist_ok=True)

    css_filename = out_path + "\\style.css"
    css_link = "https://ta.yrdsb.ca/live/students/style.css"
    css_response = session.post(css_link)

    with open(css_filename, "w", encoding='utf-8') as file:
        file.write(str(css_response.text))
    print("Downloaded current TeachAssist stylesheet at " + css_filename)

    ta_tables = soup.find_all('table')
    courses_table_rows = ta_tables[1].find_all('tr')[1:]

    logout_btn = soup.find('a')
    logout_btn['href'] = '#'

    for item in courses_table_rows:
        current_row_table_data = item.find_all('td')
        linker = UNAVAILABLE_CONST

        c_data = str(current_row_table_data[0]).split(' : ')
        code = c_data[0][6:].strip()
        course_html_file = out_subdir + "\\" + code + '.html'

        current_row_link_list = current_row_table_data[-1].find_all('a') #finds any links in the current course row
        if len(current_row_link_list) > 0:
            linkitem = current_row_link_list[0]
            linker = linkitem.get('href')
            linkitem['href'] = 'courses' + "/" + code + '.html'

        if linker is not UNAVAILABLE_CONST: # checks if the link is the "please see teacher" message
            grade_url = 'https://ta.yrdsb.ca/live/students/' + linker
            get_grade_session = session.get(grade_url)
            course_grades_soup = BeautifulSoup(get_grade_session.text, 'html.parser')

            return_button = course_grades_soup.find('a')
            return_button['href'] = '../index.html'

            linktags = course_grades_soup.find_all('link')
            for l in linktags:
                if l.get('href') == "style.css":
                    l['href'] = '../style.css'

            print("Creating snapshot for course " + code + "...")
            with open(course_html_file, "w", encoding='utf-8') as file:
                file.write(str(course_grades_soup))
            print("Snapshot for " + code + " created at " + course_html_file)

    with open(filename, "w", encoding='utf-8') as file:
        file.write(str(soup))
    print("Created index.html file for snapshot at " + filename + '\n')

    print("TA snapshot HTML files saved at " + out_path)
    print("Access the snapshot of your TeachAssist homepage with the 'index.html' file.")
    print("Images and charts won't display because programatically downloading them from the TA server will get you rate-limited.")

def write_courses(login_data, out):
    session = requests.session()
    response = session.post(TA_URL, data=login_data)

    if test_conn(response):
        html_data = response.text
        courses = get_courses(html_data, session)
        course_writer(login_data['username'], courses, out)

def get_courses(html, session):
    UNAVAILABLE_CONST = "Please see teacher for current status regarding achievement in the course"

    soup = BeautifulSoup(html, 'html.parser')
    font_list = soup.find_all('font')
    for item in font_list:
        if "Invalid Login" in str(item.text):
            print("Bad login!")
            return

    ta_tables = soup.find_all('table')
    courses_table_rows = ta_tables[1].find_all('tr')[1:]

    out = []

    for item in courses_table_rows:
        current_row_table_data = item.find_all('td')
        linker = UNAVAILABLE_CONST
        rm_text = str(current_row_table_data[0]).split('Block: ')[1].split('-')[1]

        current_row_link_list = current_row_table_data[-1].find_all('a') #finds any links in the current course row
        if len(current_row_link_list) > 0:
            linker = current_row_link_list[0].get('href')

        c_data = str(current_row_table_data[0]).split(' : ')
        c_title = ''
        if len(c_data) > 1 and c_data[1].strip() != '':
            c_title = c_data[1].strip()
            block_ind = c_title.find('\t\t\t<br/>\r\n\t\t\tBlock:')
            if block_ind != -1:
                c_title = c_title[0:block_ind].strip()

        current_course = Course(
            c_data[0][6:], # code
            c_title,
            str(current_row_table_data[0]).split('Block: ')[1].split('-')[0], # block
            rm_text[0: rm_text.index('\r')].strip(), #room
            str(current_row_table_data[1]).split('~')[0][-11:], # start date
            str(current_row_table_data[1]).split('~')[1][6:16], #end date
            False, # is_open (default false unless there is a link)
            False, # has_weights (default false unless there is a link AND weights)
            [17.5, 17.5, 17.5, 17.5, 0.0, 30.0], # course weights by default is this
            str(linker) # if there is a link to the grades, this will be the link; otherwise, this is the "please see teacher" message
            )

        if current_course.grades is not UNAVAILABLE_CONST: # checks if the link is the "please see teacher" message
            grade_url = 'https://ta.yrdsb.ca/live/students/' + current_course.grades
            get_grade_session = session.get(grade_url)
            course_grades_soup = BeautifulSoup(get_grade_session.text, 'html.parser')
            all_course_div = course_grades_soup.find('div').find_all('div', recursive=False) # find all div elements in grades page
            all_course_tables = all_course_div[1].find_all('table') # find the table elements within the div containing the grades
            grades_table = all_course_tables[1]

            all_bottom_table = all_course_div[2].find_all('table')
            weightings_table = all_bottom_table[1]

            if len(all_bottom_table) > 2:
                current_course.has_weights = True
                current_course.strand_weights = current_course.get_strand_weights(weightings_table)

            current_course.set_assignments(grades_table)
            current_course.is_open = True
            out.append(current_course)

    return out

def test_conn(response):
    status = response.status_code
    if status > 499:
        print(f"Error {str(response.status_code)}: Problem on TeachAssist's side. Try again later.")
        if status == 403:
            print("You may be rate-limited from the site. Try not to use this tool too many times within a short time frame.")
    elif status > 299:
        print(f"Error {str(response.status_code)}: Something went wrong. Check your connection or try again later.")
    else:
        print("Response from " + TA_URL + f" = {str(response.status_code)}; Success")
    return status < 300

def dir_maker(out):
    f_root = Path(os.path.dirname(os.path.realpath(__file__))).parent.absolute()
    trg = str(f_root) + out
    # print(trg)
    Path(trg).mkdir(parents=True, exist_ok=True)
    return trg
