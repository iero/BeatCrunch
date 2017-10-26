# Beatcrunch

The reader is built from flask-neaws-reader ( https://github.com/jackvz/flask-news-reader )

### Installing dependencies

- Install the Python dependencies: 
  - `pip install Flask`
  - `pip install feedparser`

### Developing

- Run `python reader.py` and open localhost:5000 in a browser 

### Deploying to Apache on a Virtual Private Server

- Install the dependencies on the VPS
- Install the Apache web server: `sudo apt-get install apache2`
- Install WSGI: `sudo apt-get install libapache2-mod-wsgi`
- Copy the code to /var/www/flask-news-reader on the VPS
- Configure Apache by moving the reader.conf file from the project root to /etc/apache2/sites-available, and then disable the default site, enable the new site and restart the web server by running:
  - `sudo a2dissite 000-default.conf`
  - `sudo a2ensite reader.conf`
  - `sudo service apache2 reload`
- Check for errors: `sudo tail -f /var/log/apache2/error.log`

### Note

Use [Python virtual environments](http://modwsgi.readthedocs.io/en/develop/user-guides/virtual-environments.html) for production
