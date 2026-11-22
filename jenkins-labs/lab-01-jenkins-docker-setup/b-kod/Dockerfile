FROM jenkins/jenkins:lts-jdk21

USER root

# Docker CLI ve Kubectl kurulumu (Jenkins container içinden Docker ve K8s yönetebilmek için)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    git && \
    install -m 0755 -d /etc/apt/keyrings && \
    curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg && \
    chmod a+r /etc/apt/keyrings/docker.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends docker-ce-cli && \
    curl -fsSL -o /usr/local/bin/kubectl "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" && \
    chmod +x /usr/local/bin/kubectl && \
    curl -fsSL -o /usr/local/bin/kind "https://kind.sigs.k8s.io/dl/v0.22.0/kind-linux-amd64" && \
    chmod +x /usr/local/bin/kind && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    git config --system --add safe.directory '*'

# Eklentiler plugins.txt dosyasından kurulur
COPY plugins.txt /usr/share/jenkins/ref/plugins.txt
RUN jenkins-plugin-cli -f /usr/share/jenkins/ref/plugins.txt

# Docker soket erişimi için izinler
RUN groupadd -for -g 999 docker 2>/dev/null || true && \
    usermod -aG docker jenkins

USER jenkins
