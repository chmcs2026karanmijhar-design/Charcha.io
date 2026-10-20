# Charcha.io — A Community Question & Answer Platform

Charcha.io is a Django-based question-and-answer web application inspired by platforms such as Quora and Stack Overflow. It provides a space where users can ask questions, share knowledge, exchange ideas, and interact with a community around different topics.

The project was developed as a college project to demonstrate full-stack web development using Django, Python, HTML, Tailwind CSS, JavaScript, and SQLite.

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Installation and Setup](#installation-and-setup)
- [Running the Application](#running-the-application)
- [Admin Panel](#admin-panel)
- [Database](#database)
- [Deployment](#deployment)
- [Team Collaboration](#team-collaboration)
- [Future Improvements](#future-improvements)

## Project Overview

Charcha.io aims to make knowledge sharing simple and interactive. Registered users can publish questions, submit answers, discuss content, follow users and topics, and discover questions through search and personalized feeds.

The application also includes community Spaces, bookmarks, notifications, answer requests, and reporting functionality to support an engaging question-and-answer experience.

## Features

### User Accounts and Profiles
- User registration, login, and logout.
- Editable user profiles.
- Profile pictures and biographies.
- Location and professional credentials.
- Follow and unfollow users.
- View followers and following counts.
- Block and unblock users.

### Questions and Answers
- Ask questions and associate them with topics.
- Add answers to questions.
- Comment on questions and answers.
- Edit and delete your own content.
- Upvote and downvote answers.
- Browse questions and their answers.

### Discovery and Personalization
- Search questions by title and content.
- Browse topics and topic-related questions.
- Follow topics and individual questions.
- View the home feed and following feed.
- Bookmark questions and access saved questions.

### Spaces and Community
- Create and browse Spaces.
- Join and leave Spaces.
- Associate Spaces with topics.
- Explore topic-related content within the community.

### Notifications and Interaction
- View notifications.
- Track relevant activity, including new answers and comments on followed questions.
- Request answers from other registered users.

### Reporting and Moderation
- Report questions and answers.
- Review reports through the Django administration panel.
- Manage report statuses through the admin interface.

### Sharing
- Share question links using available browser sharing and copying options.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Django | Backend web framework |
| SQLite | Relational database |
| HTML5 | Web page structure |
| Tailwind CSS | User interface styling |
| JavaScript | Client-side interactivity |
| Django Templates | Dynamic page rendering |
| Git and GitHub | Version control and collaboration |

## Project Structure

The project is organized into Django applications, with each app responsible for a particular part of the website.

```text
Charcha.io/
├── manage.py
├── requirements.txt
├── README.md
├── .gitignore
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── accounts/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── migrations/
├── questions/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── migrations/
├── communities/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── migrations/
├── notifications/
│   └── ...
└── templates/
    ├── accounts/
    ├── questions/
    └── communities/
```

*Note: This structure illustrates the main project components. Individual files and folders may differ slightly in the current repository.*

## Installation and Setup

### Prerequisites

Install the following before running the project:

- Python 3.12 or another compatible Python version.
- Git.
- A code editor such as Visual Studio Code.

### 1. Clone the Repository

```bash
git clone https://github.com/chmcs2026karanmijhar-design/Charcha.io.git
cd Charcha.io
```

### 2. Create a Virtual Environment

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Apply Database Migrations

```bash
python manage.py migrate
```

### 5. Create an Administrator Account

```bash
python manage.py createsuperuser
```

Follow the prompts to create your administrator username and password.

### 6. Start the Development Server

```bash
python manage.py runserver
```

Open the following URL in your browser:

http://127.0.0.1:8000/

## Admin Panel

Django provides an administration interface for managing registered users and registered application models.

After creating a superuser and starting the server, visit:

http://127.0.0.1:8000/admin/

Sign in with your superuser credentials to access the administrative interface.

## Database

The project uses SQLite as its default database.

SQLite is suitable for local development, demonstrations, and small academic projects because it requires minimal configuration.

For production deployment, database persistence and backups should be considered carefully. On hosting platforms with ephemeral filesystems, a local SQLite database may be lost when the application restarts or is redeployed unless persistent storage is configured.

## Deployment

Charcha.io can be deployed to a compatible Python hosting platform.

A typical deployment process includes:

1. Push the project to GitHub.
2. Configure the hosting service to install dependencies from `requirements.txt`.
3. Configure the appropriate build and start commands.
4. Set production environment variables securely.
5. Configure Django's production settings, including `DEBUG`, `ALLOWED_HOSTS`, and static-file handling.
6. Apply database migrations.
7. Test registration, login, questions, answers, and other core features on the deployed website.

**Security note:** Do not publish your Django secret key, passwords, or other sensitive credentials in the repository. Production deployment should use environment variables and appropriate security settings.

## Team Collaboration

This project uses Git and GitHub for source control and collaboration.

Team members can contribute by:

1. Cloning the shared repository.
2. Creating a branch or working on an agreed feature.
3. Making and testing code changes.
4. Committing changes with meaningful commit messages.
5. Pushing commits to GitHub.
6. Reviewing and integrating changes.

Each team member should use their own GitHub account and accurately represent their contributions.

## Future Improvements

Potential improvements include:

- More comprehensive enforcement of blocking across the application.
- Improved moderation and reporting workflows.
- Additional search filters and personalized recommendations.
- Automated tests for important user flows.
- Improved accessibility and responsive design.
- Production database configuration and stronger deployment security.
- Enhanced performance and error handling.

## Academic Project

**Project Name:** Charcha.io  
**Project Type:** College Web Development Project  
**Category:** Community Question & Answer Platform  
**Backend:** Django  
**Database:** SQLite  
**Frontend:** HTML, Tailwind CSS, JavaScript

---

Charcha.io — Ask questions. Share knowledge. Build community.
