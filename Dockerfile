# ---------------------------------------------------------------------------
# NOTE: Don't upgrade PODMAN_IMAGE_VERSION from v5.4 until they fix the
#       /etc/machine-id bug!
ARG PYTHON_VERSION=3.14
ARG PODMAN_IMAGE_VERSION=v5.4
FROM python:${PYTHON_VERSION} AS build

COPY src/           /var/tmp/gitlab-ci/src
COPY pyproject.toml /var/tmp/gitlab-ci/pyproject.toml
COPY uv.lock        /var/tmp/gitlab-ci/uv.lock

ENV PATH="${PATH}:~/.local/bin"
RUN curl -LsSf https://astral.sh/uv/install.sh | sh  && \
    cd /var/tmp/gitlab-ci  && \
    ~/.local/bin/uv build


# ---------------------------------------------------------------------------
FROM quay.io/podman/stable:${PODMAN_IMAGE_VERSION} AS base

# Silence this warning: Emulate Docker CLI using podman...
RUN touch /etc/containers/nodocker

# In lieu of upgrading from v5.4 (see NOTE above), we do an update here:
RUN dnf update  -y &&  \
    dnf install -y  awk  \
                    curl  \
                    git  \
                    helm  \
                    npm  \
                    python3-pip  \
                    rsync  \
                    sponge  \
                    vim

RUN curl -LsSf https://astral.sh/uv/install.sh | env UV_UNMANAGED_INSTALL="/bin" sh

COPY --from=build   /var/tmp/gitlab-ci/dist /usr/local/gitlab-ci
COPY                src/gitlab-ci.py        /opt/gitlab-ci/gitlab-ci.py

WORKDIR /opt/gitlab-ci
RUN pip3 install --root-user-action ignore /usr/local/gitlab-ci/*.whl


ENTRYPOINT ["/bin/bash", "-c"]
CMD ["/opt/gitlab-ci/gitlab-ci.py", "--help"]
