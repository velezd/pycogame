FROM ubuntu:latest

ARG DEBIAN_FRONTEND=noninteractive

RUN apt update -y
RUN apt install -y python3 cmake gcc-arm-none-eabi libnewlib-arm-none-eabi build-essential
