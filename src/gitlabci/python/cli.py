import argparse
import enum
import logging
import pathlib
import re
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
class PythonTestError(RuntimeError):
    ''' Raised when an error occurs while testing a Python project '''


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
        pyprojectToml['project']['version'] = self.version.langPythonVersion
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

    PYTEST_INI_REQUIREMENTS = {
        'pythonpath': re.compile(r'^([\S]+)$'),
        'testpaths':  re.compile(r'^([\S]+)$'),
        'junit_family': re.compile(r'^(xunit2)$'),
        'junit_suite_name': re.compile(r'^([A-Za-z0-9_ -]+)$'),
        'addopts': [
            re.compile(r'^--junitxml=(./.build/test-results/unit-tests.xml)$'),
            re.compile(r'^--cov=([\S]+)$'),
            re.compile(r'^--cov-report=(xml:./.build/test-results/coverage.xml)$'),
            re.compile(r'^--cov-report=(term)$'),
        ]
    }

    def build(self) -> list[pathlib.Path]:
        # NOTE: For uv-based project, the toml file is required
        #       Raises FileNotFoundError if the above is violated
        pyprojectToml = self._load_pyproject_toml()
        pyprojectToml['project']['version'] = self.version.langPythonVersion

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
            utils.ProcessPrinter.follow(proc, logger=LOGGER, method='info')

            if proc.returncode != 0:
                raise PythonBuildError(f'Error occured while building {self.name}:{self.version.langPythonVersion}')

        return self.artifacts

    def test(self, validate_only=False, **kwargs):
        # NOTE: For uv-based project, the toml file is required
        #       Raises FileNotFoundError if the above is violated
        pyprojectToml = self._load_pyproject_toml()
        pytest_ini = pyprojectToml.get('tool', {}).get('pytest', {}).get('ini_options')
        if not pytest_ini:
            raise PythonTestError('Project is missing PyTest configuration required for CI/CD')

        for key, value in PythonProjectUv.PYTEST_INI_REQUIREMENTS.items():
            tomlItem = pytest_ini.get(key)
            PythonProjectUv.assert_toml_setting(key, value, tomlItem)

        if validate_only:
            return

        command = [
            'uv',
            'run',
            'pytest',
        ]

        with subprocess.Popen(command,
                              cwd=self.project_root,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT,
                              encoding='utf-8') as proc:
            utils.ProcessPrinter.follow(proc, logger=LOGGER, method='info')

            if proc.returncode != 0:
                raise PythonBuildError(f'Error occured while testing {self.name}:{self.version.langPythonVersion}')



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
            utils.ProcessPrinter.follow(proc, logger=LOGGER, method='info')

            if proc.returncode != 0:
                raise PythonBuildError(f'Error occured while uploading {self.name}:{self.version.langPythonVersion}')

    @staticmethod
    def assert_toml_setting(settingName, expected, actual):
        if not actual:
            raise PythonTestError(f'Project TOML is missing required field: {settingName}')
        if isinstance(expected, re.Pattern) and isinstance(actual, str):
            PythonProjectUv._assert_toml_string_pattern(settingName, expected, actual)
        elif isinstance(expected, list) and isinstance(actual, list):
            PythonProjectUv._assert_toml_list(settingName, expected, actual)
        else:
            raise PythonTestError(f'Unexpected TOML field type: {type(actual)} (comparing to {type(expected)})')

    @staticmethod
    def _assert_toml_string_pattern(settingName, expected: re.Pattern, actual: str):
        if not expected.search(actual):
            raise PythonTestError(f'Expected {settingName} to match \'{expected.pattern}\' (actual: {actual})')
        LOGGER.debug(f'Found match for {settingName}: \'{actual}\' (expected pattern: {expected.pattern})')

    @staticmethod
    def _assert_toml_list(settingName, expected: list[re.Pattern], actual: list[str]):
        # Every item in 'expected' must somewhere be in 'actual'
        for e in expected:
            searchAll: list[re.Match] = [e.search(a) for a in actual]
            match: re.Match = next(filter(None, searchAll), None)
            if not match:
                raise PythonTestError(f'Expected {settingName} to contain \'{e.pattern}\'')
            LOGGER.debug(f'Found match for {settingName}: \'{match.group(1)}\' (expected pattern: {e.pattern})')



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
                raise PythonBuildError(f'Error occured while building {self.name}:{self.version.langPythonVersion}')

        return self.artifacts

    def test(self, **kwargs):
        raise RuntimeError('Not implemented')

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
                raise PythonBuildError(f'Error occured while uploading {self.name}:{self.version.langPythonVersion}')


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
def test(args: argparse.Namespace):
    info: Info = Info.create()
    version: PipelineVersion = VersionFactory.create()

    project = args.build_type.builder_class(args.project_name or info.projectName,
                                            pathlib.Path(args.project_root),
                                            pathlib.Path(args.output_dir),
                                            info=info,
                                            version=version)

    project.test(validate_only=args.validate_only)


# ----------------------------------------------------------------------------
def push(args: argparse.Namespace):
    info: Info = Info.create()
    version: PipelineVersion = VersionFactory.create()

    project = args.build_type.builder_class(args.project_name or info.projectName,
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


    # ----- build
    build_subparser = local_subparsers.add_parser('build',
                                                  formatter_class=rich_argparse.RichHelpFormatter)

    build_subparser.set_defaults(func=build)


    # ----- test
    test_subparser = local_subparsers.add_parser('test',
                                                 formatter_class=rich_argparse.RichHelpFormatter)
    test_subparser.add_argument('--validate-only',
                                action='store_true',
                                help='Only validate the pyproject.toml file, don\'t execute the unit tests')
    test_subparser.set_defaults(func=test)


    # ----- build
    push_subparser = local_subparsers.add_parser('push',
                                                 formatter_class=rich_argparse.RichHelpFormatter)
    push_subparser.set_defaults(func=push)


def process_cli_options(parser: argparse.ArgumentParser, args: argparse.Namespace, **kwargs):
    pass
