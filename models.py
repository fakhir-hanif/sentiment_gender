from server import db


def max_length(length):
    def validate(value):
        if len(value) <= length:
            return True
        raise Exception('%s must be at most %s characters long' % length)
    return validate

class Gender(db.Document):
    structure = {
        'f_name': unicode,
        'l_name': unicode,
        'email': unicode,
        'gender': unicode,
    }
    validators = {
        'f_name': max_length(50),
        'email': max_length(120)
    }
    use_dot_notation = True
    def __repr__(self):
        return '<User %r>' % (self.f_name)

