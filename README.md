# LyveSkin

LyveSkin is a web application designed to provide a user-friendly platform for skincare-related features. It includes user authentication, product management, and community engagement tools—all wrapped in a clean, responsive interface.

## Features

- **User Authentication** – Secure login, registration, and profile management.
- **Skincare Product Management** – Admin and users can manage product items.
- **Forum** – Community space for users to discuss skincare topics.
- **Responsive Design** – Works on desktops and mobile devices.
- **Dockerized Setup** – Easily deployable using Docker.

## Tech Stack

- **Framework**: Django (Python)
- **Frontend**: HTML, TailwindCSS, Bootstrap (optional via CDN)
- **Database**: SQLite (default) or Postgres (optional for production)
- **Containerization**: Docker & Docker Compose
- **Web Server**: Nginx (configured in production)

## Getting Started

### Prerequisites

- Python 3.10+
- Docker & Docker Compose
- Git

### Installation

1. **Clone the repository**:

    ```bash
    git clone https://github.com/melisms/lyveskin-new.git
    cd lyveskin-new
    ```

2. **Set up environment variables**:

    ```bash
    cp .env.example .env
    # Update values in .env as needed
    ```

3. **Build and start the containers**:

    ```bash
    docker-compose up --build
    ```

4. **Apply migrations and create a superuser**:

    ```bash
    docker-compose exec app python manage.py migrate
    docker-compose exec app python manage.py createsuperuser
    ```

5. **Access the app**:

    - Open your browser at: [http://localhost:8000](http://localhost:8000)

## Project Structure

```text
lyveskin-new/
├── forum/               # Forum app for community discussions
├── item/                # Item-related logic and models
├── lyve/                # Project settings and core URLs
├── media/               # Uploaded files
├── nginx/               # Nginx reverse proxy configuration
├── skinc/               # Skincare-specific functionality
├── static/              # Static assets (CSS, JS, images)
├── templates/           # HTML templates used across the app
├── users/               # User authentication and profile logic
├── .env.example         # Sample environment variables file
├── Dockerfile           # Dockerfile for containerizing the Django app
├── docker-compose.yml   # Docker Compose setup for development
├── manage.py            # Django's management script
└── requirements.txt     # Python package dependencies
```

## Useful Commands

- Run tests:  
  ```bash
  docker-compose exec app python manage.py test
  docker-compose exec app python manage.py collectstatic
  ```

## Contributing

Contributions are welcome! If you'd like to improve this project, please fork the repository, create a new branch, and open a pull request with your changes. Be sure to write clear commit messages and follow any existing code style guidelines.

## License

This project is open-source and available under the [MIT License](LICENSE).

## Contact

For support, feedback, or business inquiries, please contact: **codesblue@outlook.com**
