FROM tiangolo/uwsgi-nginx:python2.7

LABEL maintainer="Simon Gerber <gesimu@gmail.com>"

RUN pip install flask flask-login

RUN adduser --uid 1001 --ingroup root appuser && \
    mkdir -p /app/instance && \
    mkdir -p /var/supervisor && \
    chown -R appuser:root /app/instance && \
    chown -R appuser:root /var/cache/nginx && \
    chown -R appuser:root /var/log/nginx && \
    chown -R appuser:root /var/supervisor && \
    chmod -R g+w /app/instance && \
    chmod -R g+w /var/cache/nginx && \
    chmod -R g+w /var/log && \
    chmod -R g+w /var/supervisor && \
    touch /app/instance/users.txt

# provide our own supervisord config that works as non-root
COPY supervisord-service.conf /etc/supervisor/supervisord.conf

# provide our own nginx base config
COPY nginx-service.conf /etc/nginx/nginx.conf

# provide own global uwsgi.ini which works as non-root
COPY uwsgi-service.ini /etc/uwsgi/uwsgi.ini

# By default, allow unlimited file sizes, modify it to limit the file sizes
# To have a maximum of 1 MB (Nginx's default) change the line to:
# ENV NGINX_MAX_UPLOAD 1m
ENV NGINX_MAX_UPLOAD 0

# By default, Nginx listens on port 80.
# To modify this, change LISTEN_PORT environment variable.
# (in a Dockerfile or with an option for `docker run`)
ENV LISTEN_PORT 8000
EXPOSE 8000

# Which uWSGI .ini file should be used, to make it customizable
ENV UWSGI_INI /app/uwsgi.ini

# URL under which static (not modified by Python) files will be requested
# They will be served by Nginx directly, without being handled by uWSGI
ENV STATIC_URL /static
# Absolute path in where the static files wil be
ENV STATIC_PATH /app/static

# If STATIC_INDEX is 1, serve / with /static/index.html directly (or the static URL configured)
# ENV STATIC_INDEX 1
ENV STATIC_INDEX 0

# Add demo app
COPY . /app
WORKDIR /app

RUN chown appuser:root /app && \
    chmod -R g+w /app

# Make /app/* available to be imported by Python globally to better support several use cases like Alembic migrations.
ENV PYTHONPATH=/app

# Copy start.sh script that will check for a /app/prestart.sh script and run it before starting the app
COPY setup.sh /setup.sh
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh && chmod +x /setup.sh
# Do final service setup before deploying image
RUN /setup.sh

# Switch to application user for rest
USER appuser

# entry point is provided by base image
ENTRYPOINT ["/entrypoint.sh"]

# Run the start script, it will check for an /app/prestart.sh script (e.g. for migrations)
# And then will start Supervisor, which in turn will start Nginx and uWSGI
CMD ["/usr/bin/supervisord"]
