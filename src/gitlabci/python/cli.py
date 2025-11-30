import argparse
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

class PythonBuildError(RuntimeError):
    ''' Raised when an error occurs while building (packaging) a Python project '''

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

    def build(self) -> list[pathlib.Path]:
        self._update_pyproject_toml()

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
                print(stdout)
                print(stderr)
                raise PythonBuildError(f'Error occured while uploading {self.name}:{self.version.pythonicVersion}')


    @property
    def artifacts(self):
        try:
            return [p for p in self.output_dir.iterdir()]
        except FileNotFoundError:
            return []

    def _update_pyproject_toml(self) -> pathlib.Path:
        try:
            pyprojectToml = self._load_pyproject_toml()
            pyprojectToml['project']['version'] = self.version.pythonicVersion
        except FileNotFoundError:
            pyprojectToml = self._create_pyproject_toml()

        with open(self.pyproject_toml_path, 'w') as fd:
            tomlkit.dump(pyprojectToml, fd)

            return pathlib.Path(fd.name)

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
        pyprojectToml['project']['urls'] = tomlkit.array(f'["{self.info.projectUrl}"]')

        if self.info.projectDescription:
            pyprojectToml['project']['description'] = self.info.projectDescription

        readme = self.project_root / 'README.md'

        if readme.exists():
            pyprojectToml['project']['readme'] = str(readme)

        return pyprojectToml

def build(args: argparse.Namespace):
    info: Info = Info.create()
    version: PipelineVersion = VersionFactory.create()

    project = PythonProject(args.project_name or info.projectName,
                            pathlib.Path(args.project_root),
                            pathlib.Path(args.output_dir),
                            info=info,
                            version=version)

    artifacts = project.build()
    for a in artifacts:
        LOGGER.info(f'Successfully built: {a}')

def push(args: argparse.Namespace):
    info: Info = Info.create()
    version: PipelineVersion = VersionFactory.create()

    project = PythonProject(args.project_name or info.projectName,
                            pathlib.Path(args.project_root),
                            pathlib.Path(args.output_dir),
                            info=info,
                            version=version)

    project.push()

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
