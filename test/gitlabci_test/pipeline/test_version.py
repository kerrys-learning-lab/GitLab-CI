import git
import logging
import pathlib
import pytest
import yaml
import gitlabci.pipeline
import gitlabci.pipeline.version

LOGGER = logging.getLogger('test.version')

MAJOR='1'
MINOR='2'
PATCH='3'
NEXT_PATCH='4'
BRANCH_VERSION=f'{MAJOR}.{MINOR}'
TAG_VERSION=f'{MAJOR}.{MINOR}.{PATCH}'
RELEASE_BRANCH=f'test-project-{MAJOR}.{MINOR}'
RELEASE_TAG=f'test-project-{MAJOR}.{MINOR}.{PATCH}'
RELEASE_TAG_ALT=f'v{MAJOR}.{MINOR}.{PATCH}'
DEV_BRANCH='my-dev-branch'
PIPELINE_IID='42'

@pytest.fixture
def defaultPipelineInfo() -> gitlabci.pipeline.Info:
    return gitlabci.pipeline.Info.create(**{
        'CI_API_V4_URL':            'https://gitlab.westsidestreet.net/api/v4',
        'CI_BUILDS_DIR':            '/path/to/builds',
        'CI_COMMIT_AUTHOR':         'kerry.t.johnson@gmail.com',
        'CI_COMMIT_DESCRIPTION':    "This is a description of the commit, but it's not very long",
        'CI_COMMIT_MESSAGE':        "This is the commit message.",
        'CI_COMMIT_REF_NAME':       'test-project-1.2',
        'CI_COMMIT_REF_PROTECTED':  'false',
        'CI_COMMIT_REF_SLUG':       'test-project-1.2',
        'CI_COMMIT_SHA':            '2d6bf90914999c3a04072df5aa14eae41529bbcd',
        'CI_COMMIT_SHORT_SHA':      '2d6bf909',
        'CI_COMMIT_TAG_MESSAGE':    "This is the tag message",
        'CI_COMMIT_TIMESTAMP':      "2022-01-31T16:47:55Z",
        'CI_COMMIT_TITLE':          "This is the title",
        'CI_DEFAULT_BRANCH':        'main',
        'CI_JOB_ID':                '1001',
        'CI_PIPELINE_ID':           '42',
        'CI_PIPELINE_IID':          '42',
        'CI_PIPELINE_URL':          'https://sample.gitlabci.com/pipeline/url',
        'CI_PROJECT_DIR':           '/var/tmp',
        'CI_PROJECT_ID':            '5',
        'CI_PROJECT_NAME':          'test-project',
        'CI_PROJECT_NAMESPACE':     'kerrys-learning-lab',
        'CI_PROJECT_TITLE':         "Test Project",
        'CI_PROJECT_DESCRIPTION':   "This is the description of the project",
        'CI_PROJECT_URL':           'https://sample.gitlabci.com/project/5',
        'CI_REGISTRY':              'registry.gitlabci.com:8888',
        'CI_REGISTRY_IMAGE':        'registry.gitlabci.com:8888/kerrys-learning-lab/test-project',
        'CI_REGISTRY_PASSWORD':     'password',
        'CI_REGISTRY_USER':         'user',
        'CI_REPOSITORY_URL':        'https://sample.gitlabci.com/repository/url',
        'CI_SERVER_URL':            'https://sample.gilab.com',
    })

@pytest.fixture
def protectedBranchPipelineInfo(defaultPipelineInfo: gitlabci.pipeline.Info):
    defaultPipelineInfo.commitRefProtected = True
    defaultPipelineInfo.commitBranch = RELEASE_BRANCH

    return defaultPipelineInfo

@pytest.fixture
def unprotectedBranchPipelineInfo(defaultPipelineInfo: gitlabci.pipeline.Info):
    defaultPipelineInfo.commitRefProtected = False
    defaultPipelineInfo.commitRefSlug = DEV_BRANCH

    return defaultPipelineInfo

@pytest.fixture
def protectedTagPipelineInfo(defaultPipelineInfo: gitlabci.pipeline.Info):
    defaultPipelineInfo.commitRefProtected = True
    defaultPipelineInfo.commitRefName = RELEASE_TAG
    defaultPipelineInfo.commitRefSlug = RELEASE_TAG
    defaultPipelineInfo.commitTag = RELEASE_TAG

    return defaultPipelineInfo

@pytest.fixture
def unprotectedTagPipelineInfo(defaultPipelineInfo: gitlabci.pipeline.Info):
    defaultPipelineInfo.commitRefProtected = False
    defaultPipelineInfo.commitRefName = RELEASE_TAG
    defaultPipelineInfo.commitRefSlug = RELEASE_TAG
    defaultPipelineInfo.commitTag = RELEASE_TAG

    return defaultPipelineInfo

def test_release_branch_re():
    for test in [BRANCH_VERSION, RELEASE_BRANCH]:
        reMatch = gitlabci.pipeline.version.RELEASE_BRANCH_RE.match(test)
        assert reMatch is not None
        assert reMatch.group('majorMinor') == BRANCH_VERSION

def test_release_branch_re_nomatch():
    for test in ['0.', '0', 'test-project', 'test-project-1', '1.2.3-test-project']:
        reMatch = gitlabci.pipeline.version.RELEASE_BRANCH_RE.match(test)
        assert reMatch is None

def test_release_tag_re():
    for test in [TAG_VERSION, RELEASE_TAG]:
        reMatch = gitlabci.pipeline.version.RELEASE_TAG_RE.match(test)
        assert reMatch is not None
        assert reMatch.group('semver') == TAG_VERSION
        assert reMatch.group('patch') == PATCH

def test_release_tag_re_no_match():
    for test in ['0.0', '1.2.', '1.2.3-test-project']:
        reMatch = gitlabci.pipeline.version.RELEASE_TAG_RE.match(test)
        assert reMatch is None

def test_default_version_generator( defaultPipelineInfo: gitlabci.pipeline.Info):
    uut = gitlabci.pipeline.version.VersionFactory.create( defaultPipelineInfo)

    assert uut.semanticVersion == f'0.0.0-{RELEASE_BRANCH}+{PIPELINE_IID}'

def test_default_version_generator_project_semver_prefix(defaultPipelineInfo: gitlabci.pipeline.Info):
    uut = gitlabci.pipeline.version.VersionFactory.create(defaultPipelineInfo,
                                                        **{'PROJECT_SEMVER_PREFIX': '3.2.1'})

    assert uut.semanticVersion == f'3.2.1-{RELEASE_BRANCH}+{PIPELINE_IID}'

def test_default_version_generator_default_semver_prefix(defaultPipelineInfo: gitlabci.pipeline.Info):
    uut = gitlabci.pipeline.version.VersionFactory.create(defaultPipelineInfo,
                                                        **{'DEFAULT_SEMVER_PREFIX': '6.6.6'})

    assert uut.semanticVersion == f'6.6.6-{RELEASE_BRANCH}+{PIPELINE_IID}'

def test_branch_version_generator_protected(protectedBranchPipelineInfo: gitlabci.pipeline.Info,
                                            tmp_path: pathlib.Path):
    # Create a repository that can be interrogated for tags...
    protectedBranchPipelineInfo.projectDir = git.Repo.init(str(tmp_path))

    # Add and commit a file so that the repo index is valid/populated
    p = tmp_path / "hello.txt"
    p.write_text('foo', encoding="utf-8")
    protectedBranchPipelineInfo.projectDir.index.add([str(p)])
    protectedBranchPipelineInfo.projectDir.index.commit('Flobber')

    # Create tags... this will make the current patch-level '3'
    for i in range(int(PATCH) + 1):
        protectedBranchPipelineInfo.projectDir.create_tag(f'test-project-{MAJOR}.{MINOR}.{i}')

    # Create additional (not-applicable) tags
    protectedBranchPipelineInfo.projectDir.create_tag('1.2.4')
    protectedBranchPipelineInfo.projectDir.create_tag('test-project-1.3.0')
    protectedBranchPipelineInfo.projectDir.create_tag('test-project-3.2.1')

    uut = gitlabci.pipeline.version.VersionFactory.create(protectedBranchPipelineInfo)

    # Since the tag (created above) is patch level '3', the next patch level
    # will be '4'...
    assert uut.version == BRANCH_VERSION
    assert uut.semanticVersion == f'{MAJOR}.{MINOR}.{NEXT_PATCH}-rc+{PIPELINE_IID}'

def test_branch_version_generator_protected_main(protectedBranchPipelineInfo: gitlabci.pipeline.Info,
                                                 tmp_path: pathlib.Path):
    protectedBranchPipelineInfo.commitRefProtected = True
    protectedBranchPipelineInfo.commitBranch = 'main'

    # Create a repository that can be interrogated for tags...
    protectedBranchPipelineInfo.projectDir = git.Repo.init(str(tmp_path))

    # Add and commit a file so that the repo index is valid/populated
    p = tmp_path / "hello.txt"
    p.write_text('foo', encoding="utf-8")
    protectedBranchPipelineInfo.projectDir.index.add([str(p)])
    protectedBranchPipelineInfo.projectDir.index.commit('Flobber')

    uut = gitlabci.pipeline.version.VersionFactory.create(protectedBranchPipelineInfo)

    assert uut.version == 'main'
    assert uut.semanticVersion == f'0.0.0-main+{PIPELINE_IID}'

def test_branch_version_generator_unprotected(unprotectedBranchPipelineInfo: gitlabci.pipeline.Info):
    uut = gitlabci.pipeline.version.VersionFactory.create(unprotectedBranchPipelineInfo)

    assert uut.version == DEV_BRANCH
    assert uut.semanticVersion == f'0.0.0-{DEV_BRANCH}+{PIPELINE_IID}'

def test_tag_version_generator(protectedTagPipelineInfo: gitlabci.pipeline.Info):
    uut = gitlabci.pipeline.version.VersionFactory.create(protectedTagPipelineInfo)

    assert uut.version == TAG_VERSION
    assert uut.semanticVersion == TAG_VERSION

def test_tag_version_generator_short_tag(protectedTagPipelineInfo: gitlabci.pipeline.Info):
    protectedTagPipelineInfo.commitRefName = TAG_VERSION
    protectedTagPipelineInfo.commitRefSlug = TAG_VERSION
    protectedTagPipelineInfo.commitTag = TAG_VERSION
    uut = gitlabci.pipeline.version.VersionFactory.create(protectedTagPipelineInfo)

    assert uut.version == TAG_VERSION
    assert uut.semanticVersion == TAG_VERSION

def test_tag_version_generator_alt_tag(protectedTagPipelineInfo: gitlabci.pipeline.Info):
    protectedTagPipelineInfo.commitRefName = RELEASE_TAG_ALT
    protectedTagPipelineInfo.commitRefSlug = RELEASE_TAG_ALT
    protectedTagPipelineInfo.commitTag = RELEASE_TAG_ALT
    uut = gitlabci.pipeline.version.VersionFactory.create(protectedTagPipelineInfo)

    assert uut.version == TAG_VERSION
    assert uut.semanticVersion == TAG_VERSION

def test_tag_version_generator_not_semantic(protectedTagPipelineInfo: gitlabci.pipeline.Info):
    with pytest.raises(gitlabci.pipeline.version.InvalidSemanticVersion):
        protectedTagPipelineInfo.commitTag='test-project-1.3'
        gitlabci.pipeline.version.VersionFactory.create(protectedTagPipelineInfo)

def test_write_env(protectedTagPipelineInfo: gitlabci.pipeline.Info,
                   tmp_path: pathlib.Path):
    uut = gitlabci.pipeline.version.VersionFactory.create(protectedTagPipelineInfo)

    envFile = uut.write(tmp_path, 'Env')
    with open(envFile) as f:
        env = f.read()
        assert f'ARTIFACT_VERSION={uut.version}' in env
        assert f'ARTIFACT_SEMANTIC_VERSION={uut.semanticVersion}' in env

    other = gitlabci.pipeline.version.PipelineVersion.fromEnv(envFile)
    assert uut.version == other.version
    assert uut.semanticVersion == other.semanticVersion

def test_write_yaml(protectedTagPipelineInfo: gitlabci.pipeline.Info,
                    tmp_path: pathlib.Path):
    uut = gitlabci.pipeline.version.VersionFactory.create(protectedTagPipelineInfo)
    yamlFile = uut.write(tmp_path, 'yAml')
    with open(yamlFile) as f:
        versionDict = yaml.safe_load(f)
        assert versionDict['artifactVersion'] == uut.version
        assert versionDict['artifactSemanticVersion'] == uut.semanticVersion

    other = gitlabci.pipeline.version.PipelineVersion.fromYaml(yamlFile)
    assert uut.version == other.version
    assert uut.semanticVersion == other.semanticVersion


def test_write_env_invalid_format(defaultPipelineInfo: gitlabci.pipeline.Info,
                                  tmp_path: pathlib.Path):
    with pytest.raises(RuntimeError):
        uut = gitlabci.pipeline.version.VersionFactory.create(defaultPipelineInfo)

        uut.write(tmp_path, 'foo')

