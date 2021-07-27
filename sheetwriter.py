from openpyxl import load_workbook

# * license pertains only to the spreadsheet writing portion of the software. *
# 
# This software is under the MIT Licence
# ======================================
#
# Copyright (c) 2010 openpyxl
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# Odict implementation in openpyxl/writer/odict.py uses the following licence:
#
# Copyright (c) 2001-2011 Python Software Foundation
#               2011 Raymond Hettinger
# License: PYTHON SOFTWARE FOUNDATION LICENSE VERSION 2
#          See http://www.opensource.org/licenses/Python-2.0 for full terms
# Note: backport changes by Raymond were originally distributed under MIT
#       license, but since the original license for Python is more
#       restrictive than MIT, code cannot be released under its terms and
#       still adheres to the limitations of Python license.

def course_writer(std_num, courses, out):
    output_folder_path = dir_maker(out)
    output_subfolder = '\\' + std_num + ' SPREADSHEETS - Generated '
    dateformat = datetime.now().strftime("%c")
    output_subfolder += dateformat

    template_path = os.path.dirname(os.path.realpath(__file__)) + '\\template.xlsx'
    out_path = output_folder_path + output_subfolder.replace(":", "-")

    Path(out_path).mkdir(parents=True, exist_ok=True)
    for course in courses:
        if course.is_open:
            print("Generating spreadsheet for course " + course.code + "...")
            filepath_excl = course.code + ((' - ' + course.name) if course.name != '' else '') + '.xlsx'
            filename = out_path + "\\" + filepath_excl
            copyfile(template_path, filename)
            print("Writing to spreadsheet at " + filepath_excl + "...")
            workbook = load_workbook(filename=filename)
            sheet = workbook["Marks"]

            sheet["B3"] = "MARK SUMMARY FOR " + course.code

            # course
            sheet["E4"] = course.strand_weights[0]
            sheet["I4"] = course.strand_weights[1]
            sheet["M4"] = course.strand_weights[2]
            sheet["Q4"] = course.strand_weights[3]

            mul = 100 / (course.strand_weights[0] + course.strand_weights[1] + course.strand_weights[2] + course.strand_weights[3] + course.strand_weights[4])

            # term
            sheet["C4"] = course.strand_weights[0] * mul
            sheet["G4"] = course.strand_weights[1] * mul
            sheet["K4"] = course.strand_weights[2] * mul
            sheet["O4"] = course.strand_weights[3] * mul

            i = 8

            for assignment in course.grades:
                evaluate = assignment.has_ku or assignment.has_ti or assignment.has_c or assignment.has_a
                if evaluate:
                    row = str(i)
                    sheet["A" + row] = assignment.title
                    if assignment.has_ku:
                        sheet["B" + row] = assignment.knowledge[0]
                        sheet["C" + row] = assignment.knowledge[1]
                        sheet["E" + row] = assignment.knowledge[2]
                    if assignment.has_ti:
                        sheet["F" + row] = assignment.thinking[0]
                        sheet["G" + row] = assignment.thinking[1]
                        sheet["I" + row] = assignment.thinking[2]
                    if assignment.has_c:
                        sheet["J" + row] = assignment.communication[0]
                        sheet["K" + row] = assignment.communication[1]
                        sheet["M" + row] = assignment.communication[2]
                    if assignment.has_a:
                        sheet["N" + row] = assignment.application[0]
                        sheet["O" + row] = assignment.application[1]
                        sheet["Q" + row] = assignment.application[2]

                    if assignment.has_comment:
                        sheet["R" + row] = '[Comments : ' + assignment.comment + ']'
                    i += 1

            workbook.save(filename=filename)
            print("Spreadsheet for " + course.code + " saved at " + filename)
        else:
            print(course.code + " is unavailable or has been closed by the teacher. Spreadsheet will not be generated.")
    print("\nSpreadsheet outputs saved at " + out_path + ".")
    print("Culminatings and projects under the 'other' strand must be entered manually under the 'FINALS' table in the spreadsheet.")
    print("Weightings displayed in spreadsheets may not add up to 100 if work was assigned in the 'other' strand (it still should be accurate though).")
