from app import app, db
from models import Interest, Course, Lesson, CourseInterest, User
from datetime import datetime

def create_sample_courses():
    try:
        # Find admin user
        admin = User.query.filter_by(is_admin=True).first()
        if not admin:
            print("No admin user found. Please ensure an admin user exists.")
            return
        
        print(f"Found admin user: {admin.username}")
        
        # Get interests
        ml_interest = Interest.query.filter_by(name='Machine Learning').first()
        dl_interest = Interest.query.filter_by(name='Deep Learning').first()
        nlp_interest = Interest.query.filter_by(name='Natural Language Processing').first()
        
        if not (ml_interest and dl_interest and nlp_interest):
            print("Could not find required interests:")
            interests = Interest.query.all()
            print(f"Available interests: {[i.name for i in interests]}")
            return
        
        print(f"Found required interests: ML, DL, NLP")
        
        # Create courses
        courses = [
            {
                'title': 'Introduction to Machine Learning',
                'description': 'Learn the basics of machine learning algorithms and techniques.',
                'interests': [ml_interest],
                'lessons': [
                    {'title': 'What is Machine Learning?', 'content': 'Machine learning is a field of study that gives computers the ability to learn without being explicitly programmed.', 'order': 1},
                    {'title': 'Supervised Learning', 'content': 'Supervised learning is a type of machine learning where the model is trained on labeled data.', 'order': 2},
                    {'title': 'Unsupervised Learning', 'content': 'Unsupervised learning is a type of machine learning where the model is trained on unlabeled data.', 'order': 3}
                ]
            },
            {
                'title': 'Deep Learning Fundamentals',
                'description': 'Explore neural networks and deep learning architectures.',
                'interests': [dl_interest],
                'lessons': [
                    {'title': 'Neural Networks Basics', 'content': 'A neural network is a series of algorithms that endeavors to recognize underlying relationships in a set of data.', 'order': 1},
                    {'title': 'Activation Functions', 'content': 'Activation functions determine the output of a neural network model and whether a neuron will be activated or not.', 'order': 2},
                    {'title': 'Backpropagation', 'content': 'Backpropagation is an algorithm used to train neural networks by adjusting the weights based on the error rate.', 'order': 3}
                ]
            },
            {
                'title': 'Natural Language Processing with Python',
                'description': 'Learn to process and analyze text data using Python.',
                'interests': [nlp_interest, ml_interest],
                'lessons': [
                    {'title': 'Text Preprocessing', 'content': 'Text preprocessing involves cleaning and transforming text data to make it suitable for analysis.', 'order': 1},
                    {'title': 'Word Embeddings', 'content': 'Word embeddings are a type of word representation that allows words with similar meaning to have similar representation.', 'order': 2},
                    {'title': 'Sentiment Analysis', 'content': 'Sentiment analysis is the process of determining the emotional tone behind a series of words.', 'order': 3}
                ]
            }
        ]
        
        for course_data in courses:
            # Check if course already exists
            existing_course = Course.query.filter_by(title=course_data['title']).first()
            if existing_course:
                print(f"Course '{course_data['title']}' already exists")
                continue
                
            print(f"Creating course: {course_data['title']}")
            course = Course(
                title=course_data['title'],
                description=course_data['description'],
                created_by=admin.id
            )
            db.session.add(course)
            db.session.flush()  # Get the course ID
            
            # Add course-interest relationships
            for interest in course_data['interests']:
                course_interest = CourseInterest(
                    course_id=course.id,
                    interest_id=interest.id,
                    created_by=admin.id
                )
                db.session.add(course_interest)
            
            # Add lessons
            for lesson_data in course_data['lessons']:
                lesson = Lesson(
                    title=lesson_data['title'],
                    content=lesson_data['content'],
                    course_id=course.id,
                    order=lesson_data['order']
                )
                db.session.add(lesson)
        
        # Commit all changes
        db.session.commit()
        print("Successfully created courses and lessons!")
        
        # Verify created courses
        courses = Course.query.all()
        print(f"Total courses in database: {len(courses)}")
        for course in courses:
            print(f"- {course.title}")
            
    except Exception as e:
        db.session.rollback()
        print(f"Error creating courses: {e}")

if __name__ == "__main__":
    with app.app_context():
        create_sample_courses()
        print("Database setup complete.")