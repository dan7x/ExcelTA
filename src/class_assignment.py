CONST_COMMENT = '--//--'

class Assignment:
    def __init__(self, title, knowledge, thinking, communication, application, other, comment): # each in the form of [marks, out of, weight as int, does_it_exist?]
        self.title = title
        self.knowledge = knowledge
        self.has_ku = self.knowledge.pop(-1)
        self.thinking = thinking
        self.has_ti = self.thinking.pop(-1)
        self.communication = communication
        self.has_c = self.communication.pop(-1)
        self.application = application
        self.has_a = self.application.pop(-1)
        self.other = other
        self.has_o = self.other.pop(-1)
        self.comment = comment
        self.has_comment = False
        if self.comment != CONST_COMMENT:
            self.has_comment = True
