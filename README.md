# KoopaKart
### An E-commerce System Inspired by the Super Mario Universe

## Description
KoopaKart is a full-fledged e-commerce solution designed for customers to handle their orders and for staff to maintain products and user accounts. To make the mundane task of buying everyday items like bread and milk more engaging, this project places its operations in the whimsical Super Mario universe. In this world, products are represented as stars and mushrooms, while users take on the roles of brave plumbers and their helpful toads.

This project was created for educational purposes. My main priorities include:
1. **Best Practices**: Adhering to conventions and using industry-standard packages.
2. **Learning New Technologies**: Prioritizing learning over quick solutions. While this e-commerce system could have been built more simply, my goal is to explore and understand new technologies.
3. **Clarity and Accessibility**: Although I am the sole developer, I aim to document everything clearly to ensure that anyone can understand my ideas and implementations.

![Start Page](images/start_page.png)

For a detailed list of the technologies and packages used in this project, please refer to the [Technologies Used](#technologies-used) section.


## Table of Contents
- [Local Deployment](#local-deployment)
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

## Local Deployment
To set up the project locally, follow these steps:

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/KoopaKart.git
   cd KoopaKart
   ```

2. **Create the `local_settings.env` File**
   Before installing dependencies, create a `local_settings.env` file in the root directory of the project. This file will contain environment variables needed for local deployment, such as your database connection settings.

   Example content for `local_settings.env`:

   ```env
   # Local PostgreSQL configuration
   DB_NAME=ecommerce_db
   DB_USER=postgres
   DB_PASSWORD=a_secret_password
   DB_HOST=localhost
   DB_PORT=5432

   ALLOWED_HOSTS=127.0.0.1,localhost
   DEBUG=True

   POSTGRES_DB=${DB_NAME}
   POSTGRES_USER=${DB_USER}
   POSTGRES_PASSWORD=${DB_PASSWORD}

   # Optional: set DATABASE_URL for local use if needed
   DATABASE_URL=postgres://postgres:a_secret_password@localhost:5432/ecommerce_db

   DJANGO_SECRET_KEY='XXX'
   ```

   - **Explanation**:
     - `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, and `DB_PORT`: These variables store the PostgreSQL database connection settings.
     - `ALLOWED_HOSTS`: Ensures the Django app only accepts requests from specified hosts (localhost in this case).
     - `DEBUG`: Set to `True` to enable debugging during development.
     - `POSTGRES_DB`, `POSTGRES_USER`, and `POSTGRES_PASSWORD`: These are passed to Docker to set up PostgreSQL.
     - `DATABASE_URL`: This is an optional variable that specifies the database connection string.
     - `DJANGO_SECRET_KEY`: A secret key used by Django for cryptographic operations. Make sure this is kept secure. A short guide follows.

   Save the file as `local_settings.env` in the root directory of the project.

   #### Generating a Secret Key

   The `DJANGO_SECRET_KEY` in `local_settings.env` is a crucial setting for Django's security. If you don't have one, you can generate a secret key using the following command in Python:

   ```bash
   python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
   ```

   This will generate a secure random string that you can use for your `DJANGO_SECRET_KEY` in `local_settings.env`.

   Alternatively, you can use services or online tools to generate a secure key, but ensure it remains secret and is not committed to version control.


3. **Install Poetry**
   If you haven't installed Poetry yet, you can do so by running:
   ```bash
   pip install --upgrade pip
   pip install poetry
   ```

4. **Install Dependencies**
   Use Poetry to install the project's dependencies:
   ```bash
   poetry install
   ```

5. **Run the Docker Container**
   Start the PostgreSQL database container using the `make run` command. This will set up and start your database:
   ```bash
   make run
   ```

6. **Activate the Poetry Shell**
   Once the dependencies are installed, activate the Poetry virtual environment:
   ```bash
   poetry shell
   ```

7. **Run Migrations and Start the Development Server**
   Apply the migrations and start the server with the following commands:
   ```bash
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

Once the application is running, you can access the development server at [http://127.0.0.1:8000/](http://127.0.0.1:8000/). The server will be running in debug mode, so you can test your changes and see updates immediately. The PostgreSQL database will be available via the Docker container, and any changes to the database schema can be handled through Django migrations.

## Features

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
Coming soon

## Testing

To run the project's tests, follow these steps:

1. **Activate the Poetry Shell**
   If not already activated, run:
   ```bash
   poetry shell
   ```

2. **Run Tests**
   Use Django’s test framework to run all tests:
   ```bash
   python manage.py test
   ```

This will run all the tests in your project, including tests for models, views, and other Django components. You can also add specific test apps or test cases as needed.

## Contributing
I welcome suggestions and ideas for improvement. However, please note that all coding contributions are currently handled by me. If you have any feedback or feature requests, feel free to reach out!

## Disclaimer
"While Nintendo holds a special place in my heart and I've spent countless hours enjoying their delightful games and consoles, I want to clarify that I have no official affiliation with the company. References to their fantastic art are purely for educational purposes and not intended to imply any connection with this amazing brand."

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file in the project root for more details. The licenses for the individual packages used in this project can be found in their respective repositories.

## Acknowledgments
- Shani Rubovitch: Sole developer and creator of KoopaKart.
- Inspiration from the Super Mario universe for creative elements.
- The open-source community for providing valuable resources and libraries.

## Contact Information
You can reach me at [shani.rubovitch@gmail.com](mailto:shani.rubovitch@gmail.com) or through the GitHub issue tracker for any questions or feedback.
