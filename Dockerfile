FROM ubuntu:16.04
MAINTAINER "Simon Gerber <gesimu@gmail.com>"
RUN apt-get update -y
RUN apt-get install -y python python-flask python-flask-login
COPY . /app
WORKDIR /app
RUN mkdir -p /app/instance
RUN touch /app/instance/users.txt
RUN chmod 777 /app/instance
ENTRYPOINT ["python"]
CMD ["mc_challenge_mgr.py"]