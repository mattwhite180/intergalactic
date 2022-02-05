FROM python:3.10-buster AS basedependencies
ENV TZ="America/Denver"

EXPOSE 8000

WORKDIR /usr/src/app

RUN apt-get update -y \                                                                                        
    && apt-get install -y \                                                                                    
    postgresql \
    ipython3 \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip setuptools wheel
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# COPY goalserver /usr/src/app/

CMD bash django-run.sh

# CMD echo "done building server"
