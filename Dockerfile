# ---------------------------------------------------------------------------
# NOTE: Don't upgrade PODMAN_IMAGE_VERSION from v5.4 until they fix the
#       /etc/machine-id bug!
ARG PYTHON_VERSION=3.14
ARG PODMAN_IMAGE_VERSION=v5.7.1
FROM python:${PYTHON_VERSION} AS build

COPY src/           /var/tmp/gitlab-ci/src
COPY pyproject.toml /var/tmp/gitlab-ci/pyproject.toml
COPY uv.lock        /var/tmp/gitlab-ci/uv.lock

ENV PATH="${PATH}:~/.local/bin"
RUN curl -LsSf https://astral.sh/uv/install.sh | sh  && \
    cd /var/tmp/gitlab-ci  && \
    ~/.local/bin/uv build


# ---------------------------------------------------------------------------
FROM quay.io/containers/podman:${PODMAN_IMAGE_VERSION} AS base

# Silence this warning: Emulate Docker CLI using podman...
RUN touch /etc/containers/nodocker

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

# Bazelisk/Bazel
RUN dnf install -y dnf-plugins-core && \
    dnf copr enable -y dcarp/bazelisk && \
    dnf install -y bazelisk

RUN curl -LsSf https://astral.sh/uv/install.sh | env UV_UNMANAGED_INSTALL="/bin" sh

COPY --from=build   /var/tmp/gitlab-ci/dist /usr/local/gitlab-ci
COPY                src/gitlab-ci.py        /opt/gitlab-ci/gitlab-ci.py
COPY                data                    /opt/gitlab-ci/data

WORKDIR /opt/gitlab-ci
RUN pip3 install --root-user-action ignore /usr/local/gitlab-ci/*.whl
RUN ln -s /opt/gitlab-ci/gitlab-ci.py /bin/gitlab-ci

ENTRYPOINT ["/bin/bash", "-c"]
CMD ["/opt/gitlab-ci/gitlab-ci.py", "--help"]
