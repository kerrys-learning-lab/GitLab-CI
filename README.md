# GitLab CI/CD Components

A small catalog of reusable [GitLab CI/CD Components](https://docs.gitlab.com/ci/components/)
for building, testing, and publishing project artifacts on
`gitlab.westsidestreet.net`.

| Component        | Purpose                                                              |
| ---------------- | ------------------------------------------------------------------- |
| `image-pipeline` | Build, test, promote, and release an OCI/container image.           |
| `helm-pipeline`  | Package, test, push, and release a Helm chart.                      |

Both components compute a SemVer for the pipeline (see
[Versioning](#versioning--artifact-tags)) and share a common job-naming hook.

---

## Consuming a component

Add an `include: component:` entry to the consuming project's `.gitlab-ci.yml`,
pinned to a released version:

```yaml
include:
  - component: gitlab.westsidestreet.net/kerrys-learning-lab/devsecops/gitlab-ci/image-pipeline@v0.1.3
    inputs:
      image_name: my-app
```

- **Always pin a version** (`@v0.1.3`), not a moving ref like `@main`. Browse
  available versions on the project's **CI/CD Catalog** page.
- The component contributes its own jobs (and the `build` → `test` → `publish`
  → `release` → `deploy` stages) to your pipeline. You can still define
  additional jobs of your own.

### Local includes within a project

If you keep your pipeline definition in this repo (e.g. the `examples/`), you
reference the component by path instead:

```yaml
include:
  - local: templates/image-pipeline.yml
    inputs: { ... }
```

---

## `image-pipeline`

Creates these jobs (default stage in parentheses):

| Job                    | Stage     | What it does                                              |
| ---------------------- | --------- | --------------------------------------------------------- |
| `image build`          | `build`   | Builds the image and pushes an interim `build.<n>` tag.   |
| `image unit-test`      | `test`    | Builds the `unittest` target and runs it; captures JUnit. |
| `image structure-test` | `test`    | Runs Google Container Structure Test; captures JUnit.     |
| `image promote`        | `publish` | Re-tags the interim image with the real version tags.     |
| `image release`        | `release` | Creates a GitLab Release (protected tags only).           |

**Minimal usage** — builds `./Dockerfile`, unit- and structure-tests it, and
promotes on protected refs:

```yaml
include:
  - component: gitlab.westsidestreet.net/kerrys-learning-lab/devsecops/gitlab-ci/image-pipeline@v0.1.3
```

**Commonly used inputs** (see the component's `spec:inputs` for the full list):

| Input                            | Default                          | Purpose                                                          |
| -------------------------------- | -------------------------------- | ---------------------------------------------------------------- |
| `image_name`                     | project name                     | Short image name (under the project's registry path).            |
| `image_build_dockerfile`         | `Dockerfile`                     | Dockerfile path, relative to the build context.                  |
| `image_build_context`            | `.`                              | Build context directory.                                         |
| `image_build_target`             | `''`                             | Build a specific multi-stage target.                             |
| `image_build_parent_image_name`  | `''`                             | This image's parent (see [parent/child](#parentchild-images)).   |
| `image_build_needs`              | `[]`                             | DAG `needs:` for the build job.                                  |
| `image_unit_test_enabled`        | `true`                           | Build + run the `unittest` target.                               |
| `image_structure_test_enabled`   | `true`                           | Run structure tests.                                             |
| `image_structure_test_filenames` | `test/image-structure-test.yaml` | Space-separated structure-test config file(s).                   |
| `image_promote_option`           | `protected`                      | `protected` \| `force` (push on any ref) \| `skip` (never push). |
| `image_release_enabled`          | `true`                           | Create a Release on protected tags.                              |

### Parent/child images

To build a base image and a dependent image in one pipeline, point the child at
the parent and order them with `needs`. The parent's built URI is injected into
the child build as the `BASE_IMAGE` build-arg:

```yaml
include:
  - component: .../image-pipeline@v0.1.3
    inputs:
      image_name: my-app/base
      image_release_enabled: false        # only one job per pipeline makes a Release
  - component: .../image-pipeline@v0.1.3
    inputs:
      image_name: my-app/service
      image_build_parent_image_name: my-app/base
      image_build_needs: ["image build"]  # wait for the parent build job
```

> When you include the component twice, use `jobs_name_prefix`/`jobs_name_suffix`
> to keep the job names unique.

---

## `helm-pipeline`

Creates these jobs (default stage in parentheses):

| Job              | Stage     | What it does                                                  |
| ---------------- | --------- | ------------------------------------------------------------- |
| `helm package`   | `build`   | `helm dependency update` + `helm package` with the SemVer.    |
| `helm unit-test` | `test`    | Runs `helm unittest`; captures JUnit.                         |
| `helm push`      | `publish` | Pushes the packaged chart to the chart repository.            |
| `helm release`   | `release` | Creates a GitLab Release (protected tags only).               |

**Minimal usage** — packages the chart in `.`, unit-tests it, and pushes to this
project's Helm registry on protected refs:

```yaml
include:
  - component: gitlab.westsidestreet.net/kerrys-learning-lab/devsecops/gitlab-ci/helm-pipeline@v0.1.3
```

**Commonly used inputs:**

| Input                      | Default                 | Purpose                                                       |
| -------------------------- | ----------------------- | ------------------------------------------------------------- |
| `helm_chart_dir`           | `.`                     | Directory containing `Chart.yaml`.                            |
| `helm_unit_test_chart_dir` | `.`                     | Chart dir under test (differs for library charts).            |
| `helm_unit_test_file_glob` | `tests/*.tests.yaml`    | Test file glob, relative to the chart dir.                    |
| `helm_push_repo_url`       | this project's registry | Destination chart repo (defaults to the project's registry).  |
| `helm_push_option`         | `protected`             | `protected` \| `force` \| `skip`.                             |
| `helm_release_enabled`     | `true`                  | Create a Release on protected tags.                           |

---

## Shared inputs

| Input              | Default | Purpose                                                  |
| ------------------ | ------- | -------------------------------------------------------- |
| `jobs_name_prefix` | `''`    | Prefix prepended to every job name from the component.   |
| `jobs_name_suffix` | `''`    | Suffix appended to every job name from the component.    |

Use these when you include a component more than once, to keep job names unique.

---

## Advanced: environment-variable conventions

Beyond `spec:inputs`, the jobs pick up specially-named CI/CD variables. Define
them as project or job variables — no input wiring needed.

**`image-pipeline`:**

- `IMAGE_BUILD_ARG_<NAME>` → passed as `--build-arg <NAME>=<value>`.
- `IMAGE_BUILD_SECRET_FILE_<ID>` → build secret from a file path
  (`--secret id=<id>,src=<path>`); `<ID>` is lower-cased and `_`→`-`.
- `IMAGE_BUILD_SECRET_STRING_<ID>` → build secret from a literal value.
- Automatically injected build-args: `CI_COMMIT_REF_SLUG`, `CI_PIPELINE_IID`,
  `SEMANTIC_VERSION`, `RELEASE_TRAIN`.

**`helm-pipeline`:**

- `HELM_REPO_<NAME>_URL` (+ optional `_USERNAME` / `_PASSWORD`) → adds a Helm
  repo (alias `<name>`, lower-cased, `_`→`-`) before packaging, so charts with
  dependencies can resolve them.

---

## Versioning & artifact tags

The pipeline derives a SemVer from the ref:

| Ref                            | SemVer produced                                |
| ------------------------------ | ---------------------------------------------- |
| Protected tag `vX.Y.Z`         | `X.Y.Z` (release)                              |
| Protected branch `release/X.Y` | `X.Y.<next>-rc+<pipeline>` (release candidate) |
| Any other ref                  | `0.0.0-<ref-str_slug>+<pipeline>` (dev build)      |

Promoted images are tagged with the commit ref str_slug, and (where applicable) the
release-train `X.Y` and the full SemVer.

> Release tags and `release/X.Y` branches are expected to be **protected**.

---

## Testing this repo

Components and their `examples/` are exercised with
[`gitlab-ci-local`](https://github.com/firecow/gitlab-ci-local). **`git add`
all relevant files first** (it only sees tracked content):

```console
$ gitlab-ci-local --fetch-includes --cleanup --privileged
```
