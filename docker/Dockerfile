FROM ubuntu

ARG DATASAFENAME
ARG GIT_ACCESS_TOKEN
ARG PACKAGEDIR

ENV DOCKER True
ENV GIT_ACCESS_TOKEN $accessToken


# Install Git
WORKDIR root
RUN apt-get update && apt-get install -y git
RUN apt-get install nano -y
RUN apt install python3-all -y
RUN apt install python3-pip -y
RUN pip3 install --upgrade pip

# install pipenv
RUN pip3 install pipenv

# package installs
COPY ./$DATASAFENAME.json /root/.ssp/$DATASAFENAME.json
COPY ./$Pipfile $PACKAGEDIR/$Pipfile
WORKDIR $PACKAGEDIR
RUN ls -la
RUN pipenv install
RUN echo "cd $PACKAGEDIR" >> /root/.bashrc
RUN echo "pipenv shell" >> /root/.bashrc

CMD ["tail", "-f", "/dev/null"]
