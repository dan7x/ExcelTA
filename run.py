import sys, getopt
from getpass import getpass
from src.to_sheet import write_courses, write_html

OUTPUT_DIR = "\\output"

args = sys.argv
is_html_out = len(args) == 2

if len(args) > 2:
    print("bad arguments")
    sys.exit()

# user = "your student number"
# pwd = "your teachassist password"

user = input("Username: ")
pwd = getpass()
login_data = {'username': user,
              'password': pwd}

print()

if is_html_out:
    if sys.argv[1].strip() != '-x':
        print("Bad arguments. Saves to spreadsheets by default (no args). Add -x to save as html.")
        sys.exit()
    print("Taking HTML snapshot of TA for " + str(user) + '.')
    write_html(login_data, OUTPUT_DIR)
else:
    print("Writing mark spreadsheets for " + str(user) + '.')
    write_courses(login_data, OUTPUT_DIR)

print('\nFinished.')
