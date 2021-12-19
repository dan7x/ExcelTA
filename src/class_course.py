from src.class_assignment import Assignment
from bs4 import BeautifulSoup

CONSOLE_ASSIGNMENT_SEPARATOR = '\t\t----------'

class Course:
    def __init__(self, code, name, block, room, start_date, end_date, is_open, has_weights, strand_weights, grades):
        self.code = code
        self.name = name
        self.block = block.strip()
        self.room = room
        self.start_date = start_date
        self.end_date = end_date
        self.is_open = is_open
        self.has_weights = has_weights
        self.strand_weights = strand_weights # [ku, ti, comm, app, other, xm]; OVERALL pre-exams weightings
        self.strand_weights_no_exam = [] # do something with strand_weights
        self.grades = grades

    def get_strand_weights(self, weightings_table):
        weights_out = []
        inner_table_rows = weightings_table.find('table').find_all('tr')[1:]
        for row in inner_table_rows:
            weights_out.append(float(str(row.find_all('td')[-2].text).strip('%').strip()))
        return weights_out

    def set_assignments(self, grades_table): # takes in the HTML for the table of assignments for a given course
        assignment_list = []
        self.grades = grades_table.find_all(recursive=False)[1:]
        if len(self.grades) == 0:
            self.grades = []
            return None
        for assignment_row in self.grades:
            assignment_row_data = assignment_row.find_all('td',recursive=False) #all td for given row
            assignment_title = assignment_row_data[0].text
            if len(assignment_row_data) > 2:
                assignment_strand_list = [
                    assignment_row_data[1].find('table'),
                    assignment_row_data[2].find('table'),
                    assignment_row_data[3].find('table'),
                    assignment_row_data[4].find('table')
                    ]
                if len(assignment_row_data) > 5:
                    assignment_strand_list.append(assignment_row_data[5].find('table'))
                else:
                    assignment_strand_list.append(None)
                for i in range(0, len(assignment_strand_list)):
                    assignment_strand_list[i] = self.table_tool(assignment_strand_list[i])
                assignment_list.append(Assignment(
                            assignment_title,
                            assignment_strand_list[0],
                            assignment_strand_list[1],
                            assignment_strand_list[2],
                            assignment_strand_list[3],
                            assignment_strand_list[4],
                            'n/a'))
            else:
                comment_text = str(assignment_row_data[0].text).strip()
                if comment_text != '':
                    assignment_list[len(assignment_list) - 1].comment = comment_text
        self.grades = assignment_list

    def table_tool(self, inner_table): #return value of [mark, out of, weight, exists within assignment]
        if inner_table is None or "no mark" in inner_table.text:
            return [0.0, 1.0, 0.0, False]
        inner_table_data = inner_table.find('td')
        inner_table_text = str(inner_table_data.text).split('=')[0].strip().split('/')
        weighting = str(inner_table_data.find_all('font')[-1].text).strip()
        if weighting == 'no weight':
            weighting = 0.0
        else:
            weighting = float(weighting.replace('weight=', '').strip())
        return [float(inner_table_text[0].strip()), float(inner_table_text[1].strip()), weighting, True]
