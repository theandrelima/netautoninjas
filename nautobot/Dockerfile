FROM networktocode/nautobot:2.3-py3.11

USER root

RUN apt-get update && apt-get install -y --no-install-recommends \
    openssh-client \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    nautobot-device-onboarding \
    nautobot-plugin-nornir \
    nautobot-golden-config \
    nautobot-ssot \
    nornir-nautobot \
    nornir-netmiko \
    nornir-napalm \
    netmiko \
    napalm \
    pyeapi

RUN mkdir -p /opt/nautobot/media /opt/nautobot/static && \
    chown -R nautobot:nautobot /opt/nautobot/media /opt/nautobot/static

COPY --chown=nautobot:nautobot nautobot_config.py /opt/nautobot/nautobot_config.py
COPY --chown=nautobot:nautobot uwsgi.ini /opt/nautobot/uwsgi.ini

USER nautobot