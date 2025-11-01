# FlowBoard - Mini ClickUp-style Project Management System

A comprehensive project management system built with Django, HTML, CSS, and Bootstrap. Manage workspaces, projects, sprints, tasks, and team collaboration efficiently.

## Features

### Core Functionality
- **Hierarchical Structure**: Workspace → Project → Task → Subtask
- **Role-Based Access Control**: Admin, Project Manager (PM), and Member roles
- **Task Management**: Create, assign, update, and track tasks with status tracking
- **Sprint Management**: Organize tasks into sprints with progress tracking
- **Comments**: Add comments to tasks and subtasks for team collaboration
- **Notifications**: Email and SMS notifications when users are assigned to tasks
- **Role-Based Dashboards**: Customized dashboards for each user role

### User Roles
1. **Admin**
   - Full control over workspaces, projects, and users
   - Manage workspace members and their roles
   - View comprehensive statistics across all workspaces

2. **Project Manager (PM)**
   - Manage projects, tasks, and assignments within their workspace
   - Create and manage sprints
   - Track project progress and upcoming deadlines

3. **Member**
   - View all tasks in their workspace
   - Update assigned tasks and mark them as complete
   - Add comments to tasks and subtasks

## Technology Stack

- **Backend**: Django 5.2.6
- **Frontend**: HTML5, CSS3, Bootstrap 5
- **Database**: SQLite (default, easily switchable to PostgreSQL/MySQL)
- **Notifications**: Django Email Backend, Twilio for SMS (optional)

## Project Structure

```
flowboard/
├── accounts/           # User authentication and custom user model
├── workspaces/         # Workspace management
├── projects/          # Project and sprint management
├── tasks/             # Task, subtask, and comment management
├── flowboard/         # Main project settings and dashboard views
├── templates/         # HTML templates
├── static/            # CSS, JavaScript, and images
├── manage.py
└── requirements.txt
```

## Installation & Setup

### Prerequisites
- Python 3.9 or higher
- pip (Python package installer)
- Virtual environment (recommended)

### Step 1: Clone or Download the Project

```bash
cd /path/to/flowboard
```

### Step 2: Create and Activate Virtual Environment

**Windows:**
```bash
python -m venv env
env\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv env
source env/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Required packages:**
- Django==5.2.6
- twilio==8.10.0 (optional, for SMS notifications)
- pillow==10.1.0
- python-decouple==3.8

### Step 4: Configure Settings

1. **Email Configuration** (optional but recommended)

Edit `flowboard/settings.py`:

```python
# For development (emails printed to console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# For production (using Gmail)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'noreply@flowboard.com'
```

2. **SMS Configuration** (optional)

If you want SMS notifications, sign up for [Twilio](https://www.twilio.com/) and add credentials:

```python
TWILIO_ACCOUNT_SID = 'your_account_sid'
TWILIO_AUTH_TOKEN = 'your_auth_token'
TWILIO_PHONE_NUMBER = '+1234567890'
```

**Note**: SMS notifications will be skipped if Twilio is not configured.

### Step 5: Run Migrations

```bash
python manage.py migrate
```

This creates all necessary database tables.

### Step 6: Create a Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### Step 7: Run the Development Server

```bash
python manage.py runserver
```

The application will be available at: **http://127.0.0.1:8000/**

## Usage Guide

### First-Time Setup

1. **Login**: Visit http://127.0.0.1:8000/ and log in with your superuser credentials
2. **Create Workspace**: Create your first workspace (you'll automatically become admin)
3. **Add Members**: Invite team members to your workspace and assign roles
4. **Create Project**: Create a project within the workspace
5. **Create Sprint** (optional): Organize work into sprints
6. **Create Tasks**: Add tasks to projects and assign them to team members
7. **Track Progress**: Monitor progress through role-based dashboards

### Navigation

- **Dashboard**: View role-specific overview and statistics
- **Workspaces**: Manage workspaces and members
- **Projects**: View and manage projects
- **Tasks**: View and manage tasks

### Admin Panel

Django admin is available at: **http://127.0.0.1:8000/admin/**

Use this for advanced management and data viewing.

## Key Features Walkthrough

### Creating a Task

1. Navigate to a project
2. Click "Create Task"
3. Fill in:
   - Title (required)
   - Description
   - Status (To Do, In Progress, Done)
   - Due Date
   - Assign to users
4. Submit to create

**Notifications**: All assigned users will receive email (and SMS if configured) notifications.

### Managing Subtasks

1. Open a task detail page
2. Click "Add Subtask"
3. Fill in subtask details
4. Subtasks contribute to task progress percentage

### Sprint Management

1. Open a project
2. Click "Create Sprint"
3. Set sprint dates and status
4. Assign tasks to the sprint
5. Track progress in the PM dashboard

### Role-Based Dashboards

**Admin Dashboard** shows:
- All workspaces overview
- Total projects and tasks
- Overdue and upcoming tasks
- Recent activity

**PM Dashboard** shows:
- Managed projects
- Active sprints with progress
- Task statistics
- Deadlines

**Member Dashboard** shows:
- Assigned tasks
- Completion percentage
- Personal task board (To Do, In Progress, Done)
- Upcoming deadlines

## Troubleshooting

### Common Issues

**Issue**: "Module not found" errors
- **Solution**: Ensure virtual environment is activated and dependencies are installed

**Issue**: Database errors
- **Solution**: Run `python manage.py migrate` to apply migrations

**Issue**: Static files not loading
- **Solution**: Run `python manage.py collectstatic` for production

**Issue**: SMS not working
- **Solution**: Check Twilio credentials or emails will still work without SMS

**Issue**: Permission denied errors
- **Solution**: Ensure you're logged in with appropriate role (Admin/PM for certain actions)

## Development Notes

### Adding More Users

**Via Admin Panel**:
1. Go to http://127.0.0.1:8000/admin/
2. Navigate to Users
3. Click "Add User"

**Via Registration Page**:
Users can register at `/accounts/register/`

### Database Management

To reset the database:
```bash
# Delete the database file
rm db.sqlite3

# Remove migration files (keep __init__.py)
# Then run:
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### Running Tests

```bash
python manage.py test
```

## Security Considerations

**For Production Deployment:**

1. **Change SECRET_KEY**: Generate a new secret key
2. **Set DEBUG = False**: Disable debug mode
3. **Configure ALLOWED_HOSTS**: Add your domain
4. **Use PostgreSQL**: Switch from SQLite
5. **Enable HTTPS**: Use SSL certificates
6. **Secure Passwords**: Use environment variables for sensitive data
7. **Configure CSRF**: Set proper CSRF settings

## Future Enhancements

Potential features to add:
- File attachments for tasks
- Task dependencies
- Email reminders for due dates
- Activity timeline
- Task templates
- Gantt chart view
- API for mobile apps
- Real-time notifications with WebSockets

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review Django documentation: https://docs.djangoproject.com/
3. Check Bootstrap documentation: https://getbootstrap.com/

## License

This project is for educational and demonstration purposes.

## Credits

Built with:
- Django - https://www.djangoproject.com/
- Bootstrap - https://getbootstrap.com/
- Twilio - https://www.twilio.com/

---

**Happy Project Managing!** 🚀
