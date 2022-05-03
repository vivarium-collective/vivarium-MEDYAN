FROM ubuntu:20.04

WORKDIR /root/medyan
RUN mkdir input output

# Copy MEDYAN executable
COPY build/medyan .

# Install necessary libraries
RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get -y install --no-install-recommends libx11-dev

# Run MEDYAN
ENTRYPOINT ["./medyan", "-i", "/home/input", "-o", "/home/output", "-s", "/home/input/systeminput.txt"]
