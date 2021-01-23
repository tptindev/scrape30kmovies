FROM python:3.7.9
RUN mkdir -p /home/phimlau/sourcecode/scrapemovies
WORKDIR /home/phimlau/sourcecode/scrapemovies
COPY setup.txt /home/phimlau/sourcecode/scrapemovies
RUN pip install -r setup.txt
COPY