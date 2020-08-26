FROM python
WORKDIR /app
COPY ["results_converter.py", "/app/"]
RUN pip3 install pandas
RUN pip3 install numpy
ENTRYPOINT ["python", "-u", "results_converter.py"]

