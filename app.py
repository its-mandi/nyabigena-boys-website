from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
import random

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nyabigena.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Email configuration (customize these for your email provider)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'your_password'  # Replace with your email password

# Initialize extensions
db = SQLAlchemy(app)
mail = Mail(app)

# Models (Database structure)
class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)

# Generate student data for streams
def generate_students():
    # Sample student names for Form 1 - 4
    students_names = [
        "James Carter", "Sophia Hall", "Jackson Moore", "Amelia Lee", "Liam Turner",
        "Isabella Davis", "Benjamin Walker", "Charlotte Wilson", "Ethan Harris", "Avery Young",
        "Alexander Martinez", "Olivia Walker", "Daniel Johnson", "Ella Brown", "Samuel Taylor",
        "Chloe Moore", "Ryan Green", "Mason Thomas", "Madeline Scott", "William Parker",
        "Emma Davis", "Gabriel Nelson", "Lily Lewis", "Lucas White", "Zoe Adams",
        "Noah Evans", "Caleb Harris", "Charlotte Wilson", "Mia Robinson", "Wyatt Clark",
        "Emily Wright", "Aidan Mitchell", "Sophie Scott", "Jack Turner", "Megan Phillips",
        "Benjamin Carter", "Olivia Young", "Sophia Brown", "Jackson White", "Daniel Evans",
        "Lily Lewis", "Henry Thomas", "Ella Martinez", "David Phillips", "Chloe Johnson",
        "Amelia Green", "Levi Harris", "James Robinson", "Grace Wilson", "Madison Lee",
        "Mason Brown", "Ethan Walker", "Samantha Thomas", "Lucas Martin", "Samuel Green",
        "Sophie Robinson", "Isabella Lee", "Matthew Adams", "William Taylor", "Charlotte Harris",
        "Jack Green", "Ava Young", "Liam White", "Aiden Davis", "Emma Turner"
    ]

    # Grades
    grades = ['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-']

    # Create a dictionary to hold the streams and students for each form
    students_data = {}

    for form in ['form1', 'form2', 'form3', 'form4']:
        form_students = {}
        for stream in ['North', 'South', 'East', 'West', 'Central', 'Green']:
            form_students[stream] = []
            # Randomly select 10 students for each stream in the form
            for student in random.sample(students_names, 10):
                student_grade = random.choice(grades)  # Randomly assign a grade
                form_students[stream].append({"name": student, "grade": student_grade})
        students_data[form] = form_students

    return students_data

# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/admissions')
def admissions():
    return render_template('admissions.html')

@app.route('/fees')
def fees():
    return render_template('fees.html')

@app.route('/fees/structure')  # Route for the Fees Structure page
def fees_structure():
    return render_template('fees_structure.html')  # This is where your fee structure details will be added

@app.route('/fees/statement')  # Route for the Fees Statement page
def fees_statement():
    return render_template('fees_statement.html')  # This is where you will add student login and fee payments info

@app.route('/results', methods=['GET', 'POST'])
def results():
    form = request.args.get('form', 'form1')  # Default form is form1
    search_query = request.args.get('search', '')  # Get search query from the URL
    students_data = generate_students()  # Generate students with grades

    # Only show results for the selected form and its streams
    if form in students_data:
        selected_form_data = students_data[form]
    else:
        selected_form_data = {}

    # Filter students by search query (if any)
    if search_query:
        selected_form_data = {
            stream: [student for student in students_list if search_query.lower() in student['name'].lower()]
            for stream, students_list in selected_form_data.items()
        }

    return render_template('results.html', form=form, streams=selected_form_data, search_query=search_query)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        if not name or not email or not message:
            flash('All fields are required!', 'danger')
        else:
            # Save message to the database
            new_message = ContactMessage(name=name, email=email, message=message)
            db.session.add(new_message)
            db.session.commit()

            # Send confirmation email
            try:
                msg = Message(
                    subject=f"Message from {name}",
                    recipients=['school_email@example.com'],  # Replace with the school's email
                    body=f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
                )
                mail.send(msg)
                flash('Your message has been sent successfully!', 'success')
            except Exception as e:
                flash('Failed to send email. Please try again later.', 'danger')

        return redirect(url_for('contact'))
    return render_template('contact.html')

# Run the app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure database tables are created
    app.run(debug=True)
