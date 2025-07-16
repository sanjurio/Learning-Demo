from app import app, db
from models import Interest, Course, Lesson, CourseInterest, User
from datetime import datetime

def create_interests(admin_id):
    """Create basic interest categories if they don't exist"""
    interests = {
        'Machine Learning': 'The study of computer algorithms that improve automatically through experience',
        'Deep Learning': 'A subset of machine learning based on artificial neural networks',
        'Natural Language Processing': 'The ability of computers to understand and process human language',
        'Computer Vision': 'Field of AI that trains computers to interpret and understand the visual world',
        'Reinforcement Learning': 'A type of machine learning where an agent learns to make decisions through rewards'
    }

    created_interests = {}

    for name, description in interests.items():
        # Check if interest exists
        existing = Interest.query.filter_by(name=name).first()
        if existing:
            print(f"Interest '{name}' already exists")
            created_interests[name] = existing
        else:
            # Create new interest
            interest = Interest(
                name=name,
                description=description,
                created_by=admin_id
            )
            db.session.add(interest)
            db.session.flush()
            print(f"Created interest: {name}")
            created_interests[name] = interest

    db.session.commit()
    return created_interests

def create_sample_courses():
    try:
        # Find admin user
        admin = User.query.filter_by(is_admin=True).first()
        if not admin:
            print("No admin user found. Please ensure an admin user exists.")
            return

        print(f"Found admin user: {admin.username}")

        # Create or get interests
        interests = create_interests(admin.id)
        if not interests:
            print("Failed to create interests")
            return

        # Access interest objects
        ml_interest = interests.get('Machine Learning')
        dl_interest = interests.get('Deep Learning')
        nlp_interest = interests.get('Natural Language Processing')
        cv_interest = interests.get('Computer Vision')
        rl_interest = interests.get('Reinforcement Learning')
        otp_interest = interests.get('Machine Learning') # fix: using Machine Learning as placeholder for OTP interest
        distributed_interest = interests.get('Deep Learning') # fix: using Deep Learning as placeholder for distributed interest
        concurrent_interest = interests.get('Natural Language Processing') # fix: using Natural Language Processing as placeholder for concurrent interest
        telecom_interest = interests.get('Computer Vision') # fix: using Computer Vision as placeholder for telecom interest

        print(f"Found required interests: ML, DL, NLP")

        # Create courses
        courses = [
            {
                'title': 'Introduction to Machine Learning',
                'description': 'Learn the basics of machine learning algorithms and techniques. This comprehensive course covers the fundamental concepts of ML, from data preprocessing to model evaluation. Students will gain hands-on experience implementing various algorithms.',
                'cover_image_url': 'https://images.unsplash.com/photo-1555949963-aa79dcee981c?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1470&q=80',
                'interests': [ml_interest],
                'lessons': [
                    {'title': 'What is Machine Learning?', 'content': 'Machine learning is a field of study that gives computers the ability to learn without being explicitly programmed. In this lesson, we will introduce the core concepts of machine learning, its applications, and the different types of learning paradigms. We will also discuss the history of machine learning and its relationship to artificial intelligence and statistics.', 'order': 1},
                    {'title': 'Supervised Learning', 'content': 'Supervised learning is a type of machine learning where the model is trained on labeled data. This lesson covers key supervised learning algorithms including linear regression, logistic regression, decision trees, and support vector machines. We will discuss the mathematics behind these algorithms and implement them from scratch using Python and popular libraries like scikit-learn.', 'order': 2},
                    {'title': 'Unsupervised Learning', 'content': 'Unsupervised learning is a type of machine learning where the model is trained on unlabeled data. In this lesson, we will explore clustering algorithms like K-means and hierarchical clustering, as well as dimensionality reduction techniques such as Principal Component Analysis (PCA). We will apply these methods to real-world datasets to discover patterns and structure in the data.', 'order': 3}
                ]
            },
            {
                'title': 'Deep Learning Fundamentals',
                'description': 'Explore neural networks and deep learning architectures. This course delves into neural networks from the ground up, teaching you how to build, train, and optimize deep models using modern frameworks. Perfect for those looking to understand the technology behind cutting-edge AI systems.',
                'cover_image_url': 'https://images.unsplash.com/photo-1620712943543-bcc4688e7485?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1365&q=80',
                'interests': [dl_interest],
                'lessons': [
                    {'title': 'Neural Networks Basics', 'content': 'A neural network is a series of algorithms that endeavors to recognize underlying relationships in a set of data. This lesson introduces the basic building blocks of neural networks including neurons, activation functions, and forward propagation. We will build a simple neural network from scratch and understand the mathematical foundations that make these models work.', 'order': 1},
                    {'title': 'Activation Functions', 'content': 'Activation functions determine the output of a neural network model and whether a neuron will be activated or not. In this lesson, we will examine various activation functions such as sigmoid, tanh, ReLU, Leaky ReLU, and softmax. We will discuss their properties, advantages, disadvantages, and appropriate use cases. Through practical examples, you will learn how to choose the right activation function for different layers of your neural network.', 'order': 2},
                    {'title': 'Backpropagation', 'content': 'Backpropagation is an algorithm used to train neural networks by adjusting the weights based on the error rate. This lesson provides a deep dive into the mathematics of backpropagation, including the chain rule, gradient descent, and optimization techniques. We will implement backpropagation from scratch and then compare our implementation with high-level frameworks like TensorFlow and PyTorch.', 'order': 3}
                ]
            },
            {
                'title': 'Natural Language Processing with Python',
                'description': 'Learn to process and analyze text data using Python. This practical course covers everything from basic text processing to advanced NLP techniques. Students will build real-world applications including sentiment analyzers, text classifiers, and simple chatbots.',
                'cover_image_url': 'https://images.unsplash.com/photo-1518186285589-2f7649de83e0?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1374&q=80',
                'interests': [nlp_interest, ml_interest],
                'lessons': [
                    {'title': 'Text Preprocessing', 'content': 'Text preprocessing involves cleaning and transforming text data to make it suitable for analysis. In this comprehensive lesson, we will cover tokenization, stemming, lemmatization, stop word removal, and other essential preprocessing techniques. We will use popular Python libraries such as NLTK, spaCy, and TextBlob to implement these methods efficiently. By the end of this lesson, you will understand how to convert raw text into a format suitable for machine learning models.', 'order': 1},
                    {'title': 'Word Embeddings', 'content': 'Word embeddings are a type of word representation that allows words with similar meaning to have similar representation. This lesson explores various word embedding techniques including Word2Vec, GloVe, and FastText. We will train our own word embeddings on a corpus and visualize them to understand semantic relationships between words. Additionally, we will discuss how to use pre-trained embeddings in your NLP projects and how to fine-tune them for specific tasks.', 'order': 2},
                    {'title': 'Sentiment Analysis', 'content': 'Sentiment analysis is the process of determining the emotional tone behind a series of words. In this hands-on lesson, we will build a sentiment analysis model using both traditional machine learning approaches and deep learning techniques. We will work with real-world datasets like movie reviews and social media posts to train models that can accurately classify text as positive, negative, or neutral. We will also discuss challenges in sentiment analysis such as sarcasm detection and context understanding.', 'order': 3}
                ]
            },
            {
                'title': 'Computer Vision Applications',
                'description': 'Dive into practical applications of computer vision technology. This course covers image processing, object detection, face recognition, and more. You will learn to build systems that can "see" and interpret visual information from the world.',
                'cover_image_url': 'https://images.unsplash.com/photo-1509228627152-72ae9ae6848d?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1470&q=80',
                'interests': [cv_interest, dl_interest],
                'lessons': [
                    {'title': 'Image Classification', 'content': 'Image classification is the task of assigning an input image one label from a fixed set of categories. This lesson covers the fundamentals of image classification using both traditional computer vision techniques and modern convolutional neural networks (CNNs). We will implement popular architectures like AlexNet, VGG, and ResNet, and apply transfer learning to achieve high accuracy with limited training data.', 'order': 1},
                    {'title': 'Object Detection', 'content': 'Object detection is the task of detecting instances of objects of a certain class within an image. This lesson explores algorithms like YOLO (You Only Look Once), SSD (Single Shot MultiBox Detector), and Faster R-CNN. You will learn how these models simultaneously identify the location and class of multiple objects in an image, and implement them using frameworks like TensorFlow and PyTorch.', 'order': 2},
                    {'title': 'Facial Recognition Systems', 'content': 'Facial recognition systems identify or verify a person from a digital image or video frame. In this lesson, we will build a complete facial recognition system from scratch. We will cover face detection using Haar cascades and deep learning approaches, facial landmark detection, face alignment, feature extraction, and face verification/identification using techniques like Siamese networks and triplet loss. We will also discuss ethical considerations and privacy concerns related to facial recognition technology.', 'order': 3}
                ]
            },
            {
                'title': 'Reinforcement Learning for Game AI',
                'description': 'Learn how to create intelligent agents using reinforcement learning techniques. This exciting course teaches the algorithms behind self-learning AI systems like AlphaGo. Students will develop agents capable of mastering simple games and simulated environments.',
                'cover_image_url': 'https://images.unsplash.com/photo-1563227812-0ea4c22e6cc8?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1470&q=80',
                'interests': [rl_interest, ml_interest],
                'lessons': [
                    {'title': 'RL Foundations', 'content': 'Reinforcement Learning (RL) is an area of machine learning concerned with how software agents ought to take actions in an environment to maximize some notion of cumulative reward. This introductory lesson covers the key concepts of RL including the agent-environment interface, Markov Decision Processes (MDPs), policies, value functions, and the exploration-exploitation dilemma. We will implement simple environments and agents to understand these concepts in practice.', 'order': 1},
                    {'title': 'Q-Learning and Deep Q Networks', 'content': 'Q-Learning is a model-free reinforcement learning algorithm to learn the value of an action in a particular state. This lesson extends the basic Q-learning algorithm to Deep Q Networks (DQN), which use deep neural networks to approximate the Q-value function. We will implement DQN from scratch and apply it to classic control problems like CartPole and more complex Atari games using OpenAI Gym.', 'order': 2},
                    {'title': 'Policy Gradient Methods', 'content': 'Policy gradient methods are a type of reinforcement learning techniques that rely upon optimizing parametrized policies with respect to the expected return by gradient descent. This advanced lesson covers algorithms like REINFORCE, Actor-Critic, PPO (Proximal Policy Optimization), and TRPO (Trust Region Policy Optimization). We will train agents to play complex games and compare the performance of different policy gradient methods.', 'order': 3}
                ]
            },
            {
                'title': 'Introduction to Erlang',
                'description': 'Welcome to Erlang! Erlang is a programming language used to build massively scalable soft real-time systems with requirements on high availability. Some of its uses are in telecoms, banking, e-commerce, computer telephony and instant messaging.',
                'cover_image_url': 'https://example.com/erlang.jpg',
                'interests': [otp_interest],
                'lessons': [
                    {
                        'title': 'Introduction to Erlang',
                        'content': 'Welcome to Erlang! Erlang is a programming language used to build massively scalable soft real-time systems with requirements on high availability. Some of its uses are in telecoms, banking, e-commerce, computer telephony and instant messaging.',
                        'order': 1
                    },
                    {
                        'title': 'Basic Syntax and Data Types',
                        'content': 'Learn about Erlang basic syntax, atoms, numbers, strings, lists, tuples, and pattern matching fundamentals.',
                        'order': 2
                    },
                    {
                        'title': 'Functions and Modules',
                        'content': 'Understanding how to define functions, work with modules, and organize your Erlang code effectively.',
                        'order': 3
                    }
                ]
            },
            {
                'title': 'OTP and Fault-Tolerant Systems',
                'description': 'Master the Open Telecom Platform (OTP) and learn how to build fault-tolerant, distributed systems using Erlang/OTP behaviors like GenServer, Supervisor, and Application.',
                'cover_image_url': 'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?ixlib=rb-4.0.3&auto=format&fit=crop&w=1470&q=80',
                'interests': [otp_interest, distributed_interest],
                'lessons': [
                    {
                        'title': 'Introduction to OTP',
                        'content': 'Learn about the Open Telecom Platform, its design principles, and why it makes Erlang systems so robust and fault-tolerant.',
                        'order': 1
                    },
                    {
                        'title': 'GenServer Behavior',
                        'content': 'Understanding the GenServer behavior pattern for building stateful server processes in a standardized way.',
                        'order': 2
                    },
                    {
                        'title': 'Supervision Trees',
                        'content': 'Learn how to design supervision trees and implement the "let it crash" philosophy for building resilient systems.',
                        'order': 3
                    }
                ]
            },
            {
                'title': 'Concurrent Programming with Erlang',
                'description': 'Deep dive into Erlang concurrency model, lightweight processes, message passing, and the actor model. Learn to build highly concurrent applications.',
                'cover_image_url': 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?ixlib=rb-4.0.3&auto=format&fit=crop&w=1470&q=80',
                'interests': [concurrent_interest, distributed_interest],
                'lessons': [
                    {
                        'title': 'Erlang Process Model',
                        'content': 'Understanding lightweight processes in Erlang, how they differ from OS threads, and why millions of processes can run simultaneously.',
                        'order': 1
                    },
                    {
                        'title': 'Message Passing',
                        'content': 'Learn about asynchronous message passing, mailboxes, and how processes communicate in Erlang systems.',
                        'order': 2
                    },
                    {
                        'title': 'Process Linking and Monitoring',
                        'content': 'Understanding process links, monitors, and how to handle process failures gracefully in concurrent systems.',
                        'order': 3
                    }
                ]
            },
            {
                'title': 'Telecom Systems with Erlang',
                'description': 'Explore real-world telecommunications applications built with Erlang. Learn about telecom protocols, switching systems, and high-availability requirements.',
                'cover_image_url': 'https://images.unsplash.com/photo-1544197150-b99a580bb7a8?ixlib=rb-4.0.3&auto=format&fit=crop&w=1470&q=80',
                'interests': [telecom_interest, distributed_interest],
                'lessons': [
                    {
                        'title': 'Telecom Industry Overview',
                        'content': 'Understanding the telecommunications industry, its requirements for high availability, and why Erlang was created.',
                        'order': 1
                    },
                    {
                        'title': 'Switching Systems',
                        'content': 'Learn about telecom switching systems, call routing, and how Erlang handles millions of concurrent calls.',
                        'order': 2
                    },
                    {
                        'title': 'Protocol Implementation',
                        'content': 'Implementing telecom protocols in Erlang and handling real-time communication requirements.',
                        'order': 3
                    }
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
                cover_image_url=course_data.get('cover_image_url', ''),
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