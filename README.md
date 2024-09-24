# KoopaKart
### An E-commerce System Inspired by the Super Mario Universe

## Description
KoopaKart is a full-fledged e-commerce solution designed for customers to handle their orders and for staff to maintain products and user accounts. To make the mundane task of buying everyday items like bread and milk more engaging, this project places its operations in the whimsical Super Mario universe. In this world, products are represented as stars and mushrooms, while users take on the roles of brave plumbers and their helpful toads.

This project was created for educational purposes. My main priorities include:
1. **Best Practices**: Adhering to conventions and using industry-standard packages.
2. **Learning New Technologies**: Prioritizing learning over quick solutions. While this e-commerce system could have been built more simply, my goal is to explore and understand new technologies.
3. **Clarity and Accessibility**: Although I am the sole developer, I aim to document everything clearly to ensure that anyone can understand my ideas and implementations.

For a detailed list of the technologies and packages used in this project, please refer to the [Technologies Used](#technologies-used) section.


## Table of Contents
- [Installation](#installation)
- [Deployment](#deployment)
- [Usage](#usage)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Screenshots / Demo](#screenshots--demo)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)
- [Contact Information](#contact-information)

## Installation
To set up the project locally, follow these steps:

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/KoopaKart.git
   cd KoopaKart
   ```

2. **Install Poetry**
   If you haven't installed Poetry yet, you can do so by running:
   ```bash
   pip install --upgrade pip
   pip install poetry
   ```

3. **Install Dependencies**
   Use Poetry to install the project's dependencies:
   ```bash
   poetry install
   ```

4. **Set Up Your Environment Variables**
   Create a `.env` file in the root directory of the project and add your environment variables based on the following example:
   ```
   DB_NAME=your_db_name
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   DB_HOST=your_db_host
   DB_PORT=your_db_port
   DATABASE_URL=your_database_url
   ```

5. **Run Migrations and Start the Development Server**
   Run the following commands to apply migrations and start the server:
   ```bash
   poetry shell
   python manage.py migrate
   python manage.py runserver
   ```

Now, you should be able to access the application at `http://127.0.0.1:8000/`.

## Deployment

This project is deployed on Render, a cloud platform that allows you to host applications with ease. I used Render to gain hands-on experience with deploying a Django application in the cloud.

You can access the live version of KoopaKart at the following URL:
[KoopaKart Live](https://koopakart.onrender.com)

Feel free to explore the project and experience the functionality firsthand. Screenshots and additional details will be added soon!

## Usage
How to run the project, including commands to start the server and perform common tasks.

### Features

- **User Management**: Register new users, log in, and log out.
- **Permissions**: Users are categorized into four groups: Customers, Staff Workers, Shift Managers (staff with additional permissions), and Stock Workers (staff with limited permissions). Permissions are managed at the model level to ensure database integrity and at the view level to restrict access to authorized users only.
- **Product Management**: Create new products and product categories, as well as manage stock levels and pricing changes.
- **Order Management**: Create new orders (shopping carts) and manage the items within them (to be implemented soon).
- **Logging**: An extensive logging system that uses different log levels to facilitate easy debugging.

### Planned Features
1. Mock payment integration with PayPal.
2. Integration of Google authentication for simplified registration and login.
3. Usage of Redis for caching customer orders.

## Technologies Used

This project is primarily developed in Python, utilizing the Django framework to create a robust web application, with PostgreSQL as the database management system. The complete list of packages used can be found in the pyproject.toml file managed by Poetry.

Key packages include:

- **Django**: The core framework for building the web application.
- **PostgreSQL**: The database management system used for storing and managing application data.
- **Pylint**: A tool for identifying issues in code structure and maintaining quality.
- **IPython** & **IPDB**: Enhancements for debugging, providing a more user-friendly experience.
- **Colorlog**: Enables colored log messages for improved readability in the console.
- **Whitenoise**: Simplifies the handling of static files in a production environment.
- **Python-Dotenv**: Loads local `.env` files for managing environment-specific settings.
- **Factory Boy**: Facilitates clearer and more thorough testing by allowing the creation of complex test data with less repetitive code.
- **Gunicorn**: A synchronous HTTP server for serving the application in production.


## Screenshots / Demo
Visuals or links showcasing the application in action to give potential users and employers a clear idea of what to expect.

## Testing
Instructions for running tests, including any testing frameworks used and how to interpret the results.

## Contributing
Guidelines for contributing to the project, including how to submit issues or pull requests.

## Disclaimer
"While Nintendo holds a special place in my heart and I've spent countless hours enjoying their delightful games and consoles, I want to clarify that I have no official affiliation with the company. References to their fantastic art are purely for educational purposes and not intended to imply any connection with this amazing brand."

## License
Information about the licensing of the project, if applicable.

## Acknowledgments
Credits to resources, libraries, or individuals that contributed to the project.

## Contact Information
Your contact details, such as an email address or LinkedIn profile, for inquiries related to the project.
