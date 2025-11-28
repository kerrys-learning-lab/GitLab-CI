# GitLab Runner

```
$ helm  upgrade \
        --install \
        --namespace dev \
        --values ./test/helm/values.secrets.yaml \
        gitlab-runner-test \
        test/helm/
```

# Testing in the Cluster/Container

## Running the ML Flow Pipeline
```
$ gitlab-ci.py  ml \
                data \
                prepare \
                gitlabci_test.ml.data.example_data_prepare.TrainTestData
```

# Testing the Pipeline Using GitLab CI Local

**NOTE**: Be sure to `git add` all relevant files first.

```
$ gitlab-ci-local --fetch-includes \
                  --cleanup \
                  --privileged
```

