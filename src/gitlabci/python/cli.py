import argparse
import enum
import logging
import os
import pathlib
import requests
import rich_argparse
import shutil
import subprocess
import tomlkit
from .. import utils
from ..pipeline.info import Info
from ..pipeline.version import VersionFactory, PipelineVersion

LOGGER = logging.getLogger('gitlabci.python')


# ----------------------------------------------------------------------------
class PythonBuildError(RuntimeError):
    ''' Raised when an error occurs while building (packaging) a Python project '''


# ----------------------------------------------------------------------------
class PythonProject:

    def __init__(self,
                 name: str,
                 project_root: pathlib.Path,
                 output_dir: pathlib.Path,
                 info: Info|None = None,
                 version: PipelineVersion|None = None):
        self.name = name
        self.project_root = project_root
        self.output_dir = output_dir
        self.info: Info = info or Info.create()
        self.version: PipelineVersion = version or VersionFactory.create()
        self.pyproject_toml_path = pathlib.Path(self.project_root) / 'pyproject.toml'

    @property
    def artifacts(self):
        try:
            return [p for p in self.output_dir.iterdir()]
        except FileNotFoundError:
            return []

    def _load_pyproject_toml(self, create_backup=True):
        with open(self.pyproject_toml_path, 'r') as fd:
            if create_backup:
                shutil.copy2(self.pyproject_toml_path, f'{self.pyproject_toml_path}.bak')
            return tomlkit.load(fd)

    def _create_pyproject_toml(self):
        pyprojectToml = tomlkit.toml_document.TOMLDocument()
        pyprojectToml.add('project', tomlkit.table())
        pyprojectToml['project']['name'] =  self.name
        pyprojectToml['project']['version'] = self.version.pythonicVersion
        pyprojectToml['project']['urls'] = tomlkit.table()
        pyprojectToml['project']['urls']['Homepage'] = str(self.info.projectUrl)

        if self.info.projectDescription:
            pyprojectToml['project']['description'] = self.info.projectDescription

        readme = self.project_root / 'README.md'

        if readme.exists():
            pyprojectToml['project']['readme'] = str(readme)

        return pyprojectToml


# ----------------------------------------------------------------------------
class PythonProjectUv(PythonProject):

    def build(self) -> list[pathlib.Path]:
        # NOTE: For uv-based project, the toml file is required
        #       Raises FileNotFoundError if the above is violated
        pyprojectToml = self._load_pyproject_toml()
        pyprojectToml['project']['version'] = self.version.pythonicVersion

        with open(self.pyproject_toml_path, 'w') as fd:
            tomlkit.dump(pyprojectToml, fd)

        command = [
            'uv',
            'build',
            '--out-dir', str(self.output_dir),
            str(self.project_root)
        ]

        with subprocess.Popen(command,
                              cwd=self.project_root,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT,
                              encoding='utf-8') as proc:
            utils.ProcessPrinter.follow(proc, logger=LOGGER, method='debug')

            if proc.returncode != 0:
                raise PythonBuildError(f'Error occured while building {self.name}:{self.version.pythonicVersion}')

        return self.artifacts

    def push(self):
        url: str = f'{self.info.apiUrl}/projects/{self.info.projectId}/packages/pypi'
        LOGGER.debug(url)

        command = [
            'uv',
            'publish',
            '--username', self.info.registryUser,
            '--password', self.info.registryPassword.get_secret_value(),
            '--publish-url', url
        ]

        with subprocess.Popen(command,
                              cwd=self.project_root,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT,
                              encoding='utf-8') as proc:
            utils.ProcessPrinter.follow(proc, logger=LOGGER, method='debug')

            if proc.returncode != 0:
                raise PythonBuildError(f'Error occured while uploading {self.name}:{self.version.pythonicVersion}')


# ----------------------------------------------------------------------------
class PythonProjectBuiltIn(PythonProject):

    def build(self) -> list[pathlib.Path]:
        self._create_pyproject_toml()

        command = [
            'python3',
            '-m',
            'build',
            '--outdir', str(self.output_dir),
            str(self.project_root)
        ]

        with subprocess.Popen(command,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT,
                              encoding='utf-8') as proc:
            utils.ProcessPrinter.follow(proc, logger=LOGGER, method='debug')

            if proc.returncode != 0:
                raise PythonBuildError(f'Error occured while building {self.name}:{self.version.pythonicVersion}')

        return self.artifacts

    def push(self):
        url: str = f'{self.info.apiUrl}/projects/{self.info.projectId}/packages/pypi'
        env: dict = {'TWINE_USERNAME': self.info.registryUser,
                     'TWINE_PASSWORD': self.info.registryPassword.get_secret_value()}

        command = [
            'python3',
            '-m',
            'twine',
            'upload',
            '--repository-url', url
        ]
        command.extend([str(a) for a in self.artifacts])

        with subprocess.Popen(command,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT,
                              env=env,
                              encoding='utf-8') as proc:
            utils.ProcessPrinter.follow(proc, logger=LOGGER, method='debug')

            if proc.returncode != 0:
                raise PythonBuildError(f'Error occured while uploading {self.name}:{self.version.pythonicVersion}')


# ----------------------------------------------------------------------------
class BuildType(enum.StrEnum):
    UV      = "uv", PythonProjectUv
    BUILTIN = "built-in", PythonProjectBuiltIn

    def __new__(cls, value, builder_class):
        member = str.__new__(cls, value)
        member._value_ = value
        member.builder_class = builder_class
        return member

    def __str__(self):
        return self.value


# ----------------------------------------------------------------------------
def build(args: argparse.Namespace):
    info: Info = Info.create()
    version: PipelineVersion = VersionFactory.create()

    project = args.build_type.builder_class(args.project_name or info.projectName,
                                            pathlib.Path(args.project_root),
                                            pathlib.Path(args.output_dir),
                                            info=info,
                                            version=version)

    artifacts = project.build()
    for a in artifacts:
        LOGGER.info(f'Successfully built: {a}')


# ----------------------------------------------------------------------------
def push(args: argparse.Namespace):
    info: Info = Info.create()
    version: PipelineVersion = VersionFactory.create()

    project = PythonProject(args.project_name or info.projectName,
                            pathlib.Path(args.project_root),
                            pathlib.Path(args.output_dir),
                            info=info,
                            version=version)

    project.push()


# ----------------------------------------------------------------------------
def add_cli_options(parser: argparse.ArgumentParser, **kwargs):
    local_parser = kwargs['subparsers'].add_parser('python',
                                                    formatter_class=rich_argparse.RichHelpFormatter)

    local_parser.add_argument('--project-name',
                              type=str,
                              help=f'The Python project\'s name.  If not specified, uses CI_PROJECT_NAME')
    local_parser.add_argument('--project-root',
                              type=str,
                              default='.',
                              help='The root directory containing the Python project.  Default: .')
    local_parser.add_argument('--build-type',
                              type=BuildType,
                              choices=list(BuildType),
                              required=True,
                              help='The build type for the Python project (required).')
    local_parser.add_argument('--output-dir',
                              type=str,
                              default='./dist',
                              help='Location to write the Python distribution (whl/sdist).  Default: ./dist')

    local_subparsers =local_parser.add_subparsers()
    build_subparser = local_subparsers.add_parser('build',
                                                  formatter_class=rich_argparse.RichHelpFormatter)

    build_subparser.set_defaults(func=build)
    push_subparser = local_subparsers.add_parser('push',
                                                 formatter_class=rich_argparse.RichHelpFormatter)
    push_subparser.set_defaults(func=push)


def process_cli_options(parser: argparse.ArgumentParser, args: argparse.Namespace, **kwargs):
    pass
