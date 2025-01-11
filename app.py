from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Harshal@localhost:3306/course_registration'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Student(db.Model):
    student_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    total_credits = db.Column(db.Integer, default=0)

class Course(db.Model):
    course_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    credits = db.Column(db.Integer, nullable=False)
    prerequisites = db.Column(db.Integer, db.ForeignKey('course.course_id'), nullable=True)
    seats_available = db.Column(db.Integer, default=30)

class Registration(db.Model):
    reg_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.course_id'), nullable=False)


with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return "Course Registration System is Running!"




@app.route('/add_student', methods=['POST'])
def add_student():
    data = request.json
    new_student = Student(name=data['name'])
    db.session.add(new_student)
    db.session.commit()
    return jsonify({'message': 'Student added successfully!'})


@app.route('/register', methods=['POST'])
def register():
    data = request.json
    student = Student.query.get(data['student_id'])
    course = Course.query.get(data['course_id'])

    if course.prerequisites:
        prerequisite_course = Course.query.get(course.prerequisites)
        registered_courses = [r.course_id for r in Registration.query.filter_by(student_id=student.student_id).all()]
    
    if prerequisite_course.course_id not in registered_courses:
        return jsonify({'error': 'Prerequisite not met'}), 400

    
    if course.seats_available <= 0:
        return jsonify({'error': 'No seats available'}), 400

    new_registration = Registration(student_id=student.student_id, course_id=course.course_id)
    course.seats_available -= 1
    db.session.add(new_registration)
    db.session.commit()
    return jsonify({'message': 'Registration successful!'})

@app.route('/students', methods=['GET'])
def get_students():
    students = Student.query.all()
    student_list = [{'student_id': s.student_id, 'name': s.name, 'total_credits': s.total_credits} for s in students]
    return jsonify(student_list), 200


@app.route('/courses', methods=['GET'])
def get_courses():
    

    courses = Course.query.all()
    course_list = [
        {
            'course_id': row[0],
            'name': c.name,
            'credits': c.credits,
            'prerequisites': c.prerequisites,
            'seats_available': c.seats_available
        } for row in courses
    ]
    return jsonify(course_list), 200


if __name__ == '__main__':
    app.run(debug=True)