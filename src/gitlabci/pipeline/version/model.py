import dotenv
import pathlib
import pydantic
import pydantic_extra_types.semantic_version
import os
import yaml

class PipelineVersion(pydantic.BaseModel):

    FILE_FORMATS: list[str] = ['env', 'yaml']


    version: str
    ''' Version string for this Pipeline.  May or may not be semantic '''

    semanticVersion: pydantic_extra_types.semantic_version.SemanticVersion
    ''' Given a version number MAJOR.MINOR.PATCH, increment the:

        MAJOR version when you make incompatible API changes
        MINOR version when you add functionality in a backward compatible manner
        PATCH version when you make backward compatible bug fixes

        Additional labels for pre-release and build metadata are available as
        extensions to the MAJOR.MINOR.PATCH format.'''

    langPythonVersion: str
    ''' Version string suitable for Python packages (PEP-440) '''

    langPhpVersion: str
    ''' Version string suitable for PHP packages.

        Examples:
            - 1.0.0
            - v1.2.3
            - dev-foo
            - 1.0.0-dev '''

    @staticmethod
    def fromEnv(envFilePath: pathlib.Path|None = None, **kwargs) -> "PipelineVersion":
        if envFilePath:
            kwargs = dotenv.dotenv_values(envFilePath)

        kwargs = kwargs or os.environ
        return PipelineVersion(
            version=kwargs['ARTIFACT_VERSION'],
            semanticVersion=kwargs['ARTIFACT_SEMANTIC_VERSION'],
            langPythonVersion=kwargs['ARTIFACT_LANG_PYTHON_VERSION'],
            langPhpVersion=kwargs['ARTIFACT_LANG_PHP_VERSION'],
        )

    @staticmethod
    def fromYaml(yamlFilePath: pathlib.Path) -> "PipelineVersion":
        with yamlFilePath.open('r') as f:
            values = yaml.safe_load(f)
            return PipelineVersion(
                version=values['artifactVersion'],
                semanticVersion=values['artifactSemanticVersion'],
                langPythonVersion=values['artifactLangPythonVersion'],
                langPhpVersion=values['artifactLangPhpVersion'],
            )

    def write(self, path: pathlib.Path, format='env', force=False) -> pathlib.Path:
        ''' Writes the calculated pipeline version information to file.

            Supported formats: .env, .yaml '''
        try:
            if path.exists():
                if path.is_dir():
                    myPath: pathlib.Path = path / f'version.{format.lower()}'
                elif force:
                    myPath = path
                else:
                    raise FileExistsError(f'File already exists: {path}.  Use --force to overwrite.')
            else:
                myPath = path

            content = getattr(self, f'to{format.capitalize()}String')()
            with myPath.open('a', encoding='utf-8') as f:
                f.write(content)
            return myPath
        except AttributeError:
            raise RuntimeError(f'Unrecognized file format: {format}.  Should be in {self.FILE_FORMATS}')

    def toEnvString(self):
        s  = f'ARTIFACT_VERSION={self.version}\n'
        s += f'ARTIFACT_SEMANTIC_VERSION={self.semanticVersion}\n'
        s += f'ARTIFACT_LANG_PYTHON_VERSION={self.langPythonVersion}\n'
        s += f'ARTIFACT_LANG_PHP_VERSION={self.langPhpVersion}\n'
        return s

    def toYamlString(self):
        return yaml.dump({'artifactVersion': self.version,
                          'artifactSemanticVersion': str(self.semanticVersion),
                          'artifactLangPythonVersion': self.langPythonVersion,
                          'artifactLangPhpVersion': self.langPhpVersion},
                          default_flow_style=False)
