FROM debian:bullseye

COPY libfaudio0_20.01-0~buster_i386.deb /
RUN set -eux;\
    apt-get update;\
    apt-get install -y wget gnupg2 xvfb gnutls-bin;\
    wget https://dl.winehq.org/wine-builds/winehq.key;\
    apt-key add winehq.key;\
    dpkg --add-architecture i386;\
    apt-get update;\
    echo "deb https://dl.winehq.org/wine-builds/debian/ bullseye main" >> /etc/apt/sources.list;\
    apt-get update;\
    apt-get install --install-recommends -y winehq-stable

COPY 000005CA-EA45-9AA2-D6BA-9A936376E459.dataLog /
COPY Tool.exe /
ENTRYPOINT [ "xvfb-run", "-a", "wine", "Tool.exe", "000005CA-EA45-9AA2-D6BA-9A936376E459.dataLog", "000005CA-EA45-9AA2-D6BA-9A936376E459.dataLog.csv", "J", "I", "G" ]
