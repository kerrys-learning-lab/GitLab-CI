# ============================================================================
ARG PODMAN_IMAGE_VERSION=v5.8.2
FROM quay.io/containers/podman:${PODMAN_IMAGE_VERSION} AS base

ENV INSTALL_DIR=/usr/local/install

# Silence this warning: Emulate Docker CLI using podman...
RUN touch /etc/containers/nodocker


# ----------------------------------------------------------------------------
# Prereq packages:
RUN dnf update  -y &&  \
    dnf install -y  awk  \
                    curl  \
                    file  \
                    git  \
                    helm  \
                    npm  \
                    python3-pip  \
                    rsync  \
                    skopeo  \
                    sponge  \
                    tree  \
                    vim


# ----------------------------------------------------------------------------
# Fuse overlay is not available when running nested Podman
RUN sed -i 's/driver = "overlay"/driver = "vfs"/g' /etc/containers/storage.conf

ENV HELM_URL=https://get.helm.sh
ENV HELM_VERSION=v4.2.0
ENV HELM_UNITTEST_PLUGIN_URL=https://github.com/helm-unittest/helm-unittest.git
ENV HELM_PUSH_PLUGIN_URL=https://github.com/chartmuseum/helm-push
RUN mkdir -p ${INSTALL_DIR}/helm-${HELM_VERSION}  && \
    cd ${INSTALL_DIR}/helm-${HELM_VERSION} && \
    curl -sSLO ${HELM_URL}/helm-${HELM_VERSION}-linux-amd64.tar.gz  && \
    tar --extract --auto-compress --file helm-${HELM_VERSION}-linux-amd64.tar.gz  && \
    ln -s ${INSTALL_DIR}/helm-${HELM_VERSION}/linux-amd64/helm  /usr/local/bin/helm  && \
    helm plugin install --verify=false ${HELM_UNITTEST_PLUGIN_URL}  && \
    helm plugin install --verify=false ${HELM_PUSH_PLUGIN_URL}


# ----------------------------------------------------------------------------
# Google Container Structure Test (CST)
# Ref: https://github.com/GoogleContainerTools/container-structure-test/tags
ENV CST_URL=https://github.com/GoogleContainerTools/container-structure-test
ENV CST_VERSION=v1.22.1
RUN curl -sSLO ${CST_URL}/releases/download/${CST_VERSION}/container-structure-test-linux-amd64 && \
    chmod +x container-structure-test-linux-amd64 && \
    sudo mv container-structure-test-linux-amd64 /usr/local/bin/container-structure-test


# ----------------------------------------------------------------------------
# GitLab CLI Tool (GLab)
ENV GLAB_VERSION=1.102.0
ENV GLAB_URL=https://gitlab.com/gitlab-org/cli/-/releases/v${GLAB_VERSION}/downloads/glab_${GLAB_VERSION}_linux_amd64.rpm
RUN dnf install --assumeyes ${GLAB_URL}
