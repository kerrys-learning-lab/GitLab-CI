import argparse
import datetime
import git
import git.exc
import logging
import os
import pathlib
import pydantic
import rich_argparse
from rich.console import Console as RichConsole
from rich.table import Table as RichTable

LOGGER = logging.getLogger('gitlab.info')

class Info(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    DEFAULT_LOGGABLE_ATTRS: list[str] = [
        'projectName',
        'commitTitle',
        'commitAuthor',
        'commitRefName',
        'commitRefProtected',
        'commitTimestamp',
        'pipelineIid',
        'registryImage',
    ]

    HIDDEN: list[str] = [
        'HIDDEN',
        'DEFAULT_LOGGABLE_ATTRS',
    ]

    apiUrl: pydantic.HttpUrl
    ''' The GitLab API v4 root URL '''

    commitAuthor: pydantic.EmailStr
    ''' The author of the commit in Name <email> format. '''


    commitBranch: str | None
    ''' The commit branch name.

        Available in branch pipelines, including pipelines for the default
        branch. Not available in merge request pipelines or tag pipelines.
        '''


    commitDescription: str
    ''' The description of the commit.

        If the title is shorter than 100 characters, the message without the
        first line. '''


    commitMessage: str
    ''' The full commit message. '''


    commitRefName: str
    ''' The branch or tag name for which project is built. '''


    commitRefProtected: bool
    ''' true if the job is running for a protected reference, false
        otherwise. '''


    commitRefSlug: str
    ''' CI_COMMIT_REF_NAME in lowercase, shortened to 63 bytes, and with
        everything except 0-9 and a-z replaced with -. No leading /
        trailing -. Use in URLs, host names and domain names. '''


    commitSha: str
    ''' The commit revision the project is built for. '''


    commitShortSha: str
    ''' The first eight characters of CI_COMMIT_SHA. '''


    commitTag: str | None
    ''' The commit tag name. Available only in pipelines for tags. '''


    commitTagMessage: str | None
    '''' The commit tag message. Available only in pipelines for tags. '''


    commitTimestamp: datetime.datetime
    ''' The timestamp of the commit in the ISO 8601 format.
        For example, 2022-01-31T16:47:55Z. UTC by default. '''


    commitTitle: str
    ''' The title of the commit.

        The full first line of the message. '''


    defaultBranch: str
    ''' The name of the project's default branch. '''


    jobId: str
    ''' The internal ID of the job, unique across all jobs in the GitLab
        instance. '''


    pipelineId: str
    ''' The instance-level ID of the current pipeline. This ID is unique across
        all projects on the GitLab instance. '''


    pipelineIid: str
    ''' The project-level IID (internal ID) of the current pipeline. This
        ID is unique only in the current project. '''


    pipelineUrl: pydantic.HttpUrl
    ''' The URL for the pipeline details. '''


    projectDir: git.Repo | pathlib.Path
    ''' The full path the repository is cloned to, and where the job runs from.

        If the GitLab Runner builds_dir parameter is set, this variable is set
        relative to the value of builds_dir. For more information, see the
        Advanced GitLab Runner configuration. '''


    projectId: str
    ''' The ID of the current project. This ID is unique across all
        projects on the GitLab instance. '''


    projectName: str
    ''' The name of the directory for the project. For example if the
        project URL is gitlab.example.com/group-name/project-1,
        CI_PROJECT_NAME is project-1. '''


    projectNamespace: str
    ''' The project namespace (username or group name) of the job. '''


    projectTitle: str
    ''' The human-readable project name as displayed in the GitLab web
        interface. '''


    projectDescription: str
    ''' The project description as displayed in the GitLab web interface.
        Introduced in GitLab 15.1. '''


    projectUrl: pydantic.HttpUrl
    ''' The HTTP(S) address of the project. '''


    registry: str
    ''' Address of the container registry server, formatted as <host>[:<port>].

        For example: registry.gitlab.example.com. Only available if the
        container registry is enabled for the GitLab instance. '''


    registryImage: str
    ''' Base address for the container registry to push, pull, or tag
        project’s images, formatted as <host>[:<port>]/<project_full_path>.

        For example: registry.gitlab.example.com/my_group/my_project. Image
        names must follow the container registry naming convention. Only
        available if the container registry is enabled for the project. '''


    registryPassword: pydantic.SecretStr
    ''' The password to push containers to the GitLab project's container
        registry.

        Only available if the container registry is enabled for the
        project. This password value is the same as the CI_JOB_TOKEN and is
        valid only as long as the job is running. Use the
        CI_DEPLOY_PASSWORD for long-lived access to the registry '''


    registryUser: str
    ''' The username to push containers to the project's GitLab container
        registry. Only available if the container registry is enabled for
        the project. '''


    repositoryUrl: pydantic.HttpUrl
    ''' The full path to Git clone (HTTP) the repository with a CI/CD job
        token, in the format
        https://gitlab-ci-token:$CI_JOB_TOKEN@gitlab.example.com/my-group/my-project.git. '''


    serverUrl: pydantic.HttpUrl
    ''' The base URL of the GitLab instance, including protocol and port.

        For example https://gitlab.example.com:8080. '''


    @staticmethod
    def create(**kwargs):
        kwargs = kwargs or os.environ

        # For testing, allow CI_PROJECT_DIR to point to a location that isn't
        # a valid Git repository
        try:
            projectDir = git.Repo(kwargs['CI_PROJECT_DIR'])
        except git.exc.InvalidGitRepositoryError:
            projectDir = pathlib.Path(kwargs['CI_PROJECT_DIR'])

        return Info(
            apiUrl=kwargs['CI_API_V4_URL'],
            commitAuthor=kwargs['CI_COMMIT_AUTHOR'],
            commitBranch=kwargs.get('CI_COMMIT_BRANCH'),
            commitRefProtected=kwargs.get('CI_COMMIT_REF_PROTECTED', False),
            commitDescription=kwargs['CI_COMMIT_DESCRIPTION'],
            commitMessage=kwargs['CI_COMMIT_MESSAGE'],
            commitRefName=kwargs['CI_COMMIT_REF_NAME'],
            commitRefSlug=kwargs['CI_COMMIT_REF_SLUG'],
            commitSha=kwargs['CI_COMMIT_SHA'],
            commitShortSha=kwargs['CI_COMMIT_SHORT_SHA'],
            commitTag=kwargs.get('CI_COMMIT_TAG'),
            commitTagMessage=kwargs.get('CI_COMMIT_TAG_MESSAGE'),
            commitTimestamp=kwargs['CI_COMMIT_TIMESTAMP'],
            commitTitle=kwargs['CI_COMMIT_TITLE'],
            defaultBranch=kwargs['CI_DEFAULT_BRANCH'],
            jobId=kwargs['CI_JOB_ID'],
            pipelineId=kwargs['CI_PIPELINE_ID'],
            pipelineIid=kwargs['CI_PIPELINE_IID'],
            pipelineUrl=kwargs['CI_PIPELINE_URL'],
            projectDir=projectDir,
            projectId=kwargs['CI_PROJECT_ID'],
            projectName=kwargs['CI_PROJECT_NAME'],
            projectNamespace=kwargs['CI_PROJECT_NAMESPACE'],
            projectTitle=kwargs['CI_PROJECT_TITLE'],
            projectDescription=kwargs['CI_PROJECT_DESCRIPTION'],
            projectUrl=kwargs['CI_PROJECT_URL'],
            registry=kwargs['CI_REGISTRY'],
            registryImage=kwargs['CI_REGISTRY_IMAGE'],
            registryPassword=kwargs['CI_REGISTRY_PASSWORD'],
            registryUser=kwargs['CI_REGISTRY_USER'],
            repositoryUrl=kwargs['CI_REPOSITORY_URL'],
            serverUrl=kwargs['CI_SERVER_URL'],
        )

    def logToConsole(self, attrs: list[str] | None = None, all=False, table=None):
        if table is None:
            table = RichTable(title="GitLab CI Pipeline Information")

            table.add_column("Name", justify="left", style="cyan", no_wrap=True)
            table.add_column("Value", justify="right", style="green")

        attrs = self.__dict__.keys() if all else attrs or self.DEFAULT_LOGGABLE_ATTRS

        for attrName in attrs:
            if attrName not in self.HIDDEN:
                table.add_row(attrName, str(getattr(self, attrName)))

        console = RichConsole()
        console.print(table)

def info_main(_: argparse.Namespace):
    _info = Info.create()
    _info.logToConsole()

def add_cli_options(_: argparse.ArgumentParser, **kwargs):
    info_parser = kwargs['subparsers'].add_parser('info',
                                                  formatter_class=rich_argparse.RichHelpFormatter)
    info_parser.set_defaults(func=info_main)

def process_cli_options(parser: argparse.ArgumentParser, _: argparse.Namespace, **kwargs):
    ''' Performs post-processing of CLI options, as necessary '''
    # N/A