ARG PODMAN_IMAGE_VERSION=v5.7.1

# ============================================================================
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

# ----------------------------------------------------------------------------
# Ansible
RUN dnf install -y  ansible  \
                    ansible-collection-ansible-posix  \
                    ansible-collection-community-general  \
                    ansible-collection-kubernetes-core  \
                    ansible-lint  \
                    openssh-clients


# ----------------------------------------------------------------------------
# Bazelisk/Bazel (C++ builds)
RUN dnf install -y dnf-plugins-core && \
    dnf copr enable -y dcarp/bazelisk && \
    dnf install -y bazelisk

# ----------------------------------------------------------------------------
# UV (Python package/project management)
RUN curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR="/bin" UV_NO_MODIFY_PATH=1 UV_PRINT_QUIET=1 sh

# ----------------------------------------------------------------------------
# GitLab CI tool (this repo)
COPY src/           /var/tmp/gitlab-ci/src
COPY pyproject.toml /var/tmp/gitlab-ci/pyproject.toml
COPY uv.lock        /var/tmp/gitlab-ci/uv.lock

# ----------------------------------------------------------------------------
RUN cd /var/tmp/gitlab-ci  && \
    uv build


# ============================================================================
FROM base AS final
COPY --from=base    /var/tmp/gitlab-ci/dist /usr/local/gitlab-ci
COPY                src/gitlab-ci.py        /opt/gitlab-ci/gitlab-ci.py
COPY                data                    /opt/gitlab-ci/data

WORKDIR /opt/gitlab-ci
RUN pip3 install --root-user-action ignore /usr/local/gitlab-ci/*.whl
RUN ln -s /opt/gitlab-ci/gitlab-ci.py /bin/gitlab-ci

ENTRYPOINT ["/bin/bash", "-c"]
CMD ["/opt/gitlab-ci/gitlab-ci.py", "--help"]
