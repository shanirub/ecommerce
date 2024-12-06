(no longer relevant. see README for local deployment guide)


## PostgreSQL Installation and Setup for Ecommerce Project

The `ecommerce` project uses PostgreSQL as its database. To set it up correctly, ensure PostgreSQL is installed and configured according to the following instructions. These steps are intended for Fedora Linux but should work for other distributions with minimal adjustments.

**Note**: You can use custom values for database name, user, and password. However, these should be consistent with the settings in your local environment file (`local_settings.env`).

### Steps

1. **Install Required Packages**

   Install PostgreSQL and the setup utility:

   ```bash
   sudo dnf install postgresql postgresql-server
   ```

2. **Initialize the Database**

   Initialize the PostgreSQL database:

   ```bash
   sudo postgresql-setup --initdb
   ```

3. **Start and Enable PostgreSQL Service**

   Start the PostgreSQL service and enable it to start on boot:

   ```bash
   sudo systemctl start postgresql
   sudo systemctl enable postgresql
   ```

4. **Create Database and User**

   First, access PostgreSQL as the `postgres` user:

   ```bash
   sudo -u postgres psql
   ```

   Then, in the PostgreSQL shell, execute the following commands to create the database and user:

   ```sql
   CREATE DATABASE ecommerce_db;
   CREATE USER ecommerce_user WITH PASSWORD 'password';
   GRANT ALL PRIVILEGES ON DATABASE ecommerce_db TO ecommerce_user;
   \q
   ```

5. **Change Authentication Method to `md5`**

   Edit PostgreSQL’s authentication file to change the default `ident` authentication method to `md5`:

   ```bash
   sudo vim /var/lib/pgsql/data/pg_hba.conf
   ```

   Inside `vim`, replace all occurrences of `ident` with `md5` under the appropriate section (typically near the bottom). Then, save and exit.

6. **Restart PostgreSQL Service**

   Restart the PostgreSQL service to apply changes:

   ```bash
   sudo systemctl restart postgresql
   ```

7. **Create Local Environment File**

   Create a file named `local_settings.env` (or another name of your choice, adjusting the path in `settings.py` accordingly) and add the following configuration. **If you choose other values for database settings or user credentials, ensure they match the values used in step 4.**

   ```env
   # Local PostgreSQL configuration
   DB_NAME=ecommerce_db
   DB_USER=ecommerce_user
   DB_PASSWORD=password
   DB_HOST=localhost
   DB_PORT=5432

   ALLOWED_HOSTS=127.0.0.1,localhost
   DEBUG=True

   # Optional: set DATABASE_URL for local use if needed
   DATABASE_URL=postgres://ecommerce_user:password@localhost:5432/ecommerce_db

   DJANGO_SECRET_KEY='<YOUR_SECRET_KEY>'
   ```

   - **Note**: For `DJANGO_SECRET_KEY`, generate a secure, random key. You can use this command to create one:

     ```bash
     python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
     ```

8. **Apply Migrations**

   Run Django migrations to ensure the database schema is up-to-date:

   ```bash
   python manage.py migrate
   ```
