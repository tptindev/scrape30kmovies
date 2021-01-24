FROM python:3.7.9
RUN mkdir -p /home/phimlau/app
WORKDIR /home/phimlau/app
COPY setup.txt /home/phimlau/app
RUN pip install -r setup.txt
COPY . /home/phimlau/app
CMD ["python3", "./scrape.py"]