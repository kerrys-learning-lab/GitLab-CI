# ---------------------------------------------------------------------------
FROM quay.io/podman/stable:v5.4 AS base

# Silince this warning: Emulate Docker CLI using podman...
RUN touch /etc/containers/nodocker

RUN dnf update  -y &&  \
    dnf install -y  awk  \
                    curl  \
                    git  \
                    helm  \
                    npm  \
                    rsync  \
                    sponge

RUN groupadd --gid 1001  \
             gitlab-ci   && \
    useradd  --gid 1001  \
             --uid 1001  \
             --shell /bin/bash  \
             --home-dir /opt/gitlab-ci  \
             gitlab-ci

COPY --chown=1001:1001 python/pyproject.toml  /opt/gitlab-ci/pyproject.toml
COPY --chown=1001:1001 python/src/            /opt/gitlab-ci/src

RUN ln -s /opt/gitlab-ci/gitlab-ci.py /bin/gitlab-ci

USER gitlab-ci
RUN curl -LsSf https://astral.sh/uv/install.sh | sh


ENV PYTHONPATH=/opt/gitlab-ci

WORKDIR /opt/gitlab-ci

ENTRYPOINT ["/bin/bash", "-c"]

# ---------------------------------------------------------------------------
FROM base AS test

COPY test/  /opt/gitlab-ci/test

RUN dnf install -y  python3-pytest  \
                    python3-pytest-cov

ENV PYTHONPATH=/opt/gitlab-ci:/opt/gitlab-ci/test

ENTRYPOINT ["/usr/bin/pytest"]
CMD [  \
  "--junitxml", "/var/tmp/unit-tests.xml"  \
]

# Test coverage disabled for now:
# "--cov-report", "term",  \
# "--cov-report", "xml:/var/tmp/test-coverage.xml",  \
# "--cov-fail-under=75",  \
# "--cov=gitlabci"  \

# ---------------------------------------------------------------------------
FROM base AS production

