import json
import pathlib
import requests
import tempfile
from .. import utils

class Module:
  def __init__(self, name: str, module_base: str|None = None, module_template: str|None = None):
    self.module_base = module_base or 'modules'
    self.name = name
    self.module_path = pathlib.Path(self.module_base) / self.name
    self.module_metadata_filepath = self.module_path / 'metadata.json'
    self.module_bazelfile_template = self.module_path / 'MODULE.bazel.template'

    self.module_metadata = {}

    try:
      with open(self.module_metadata_filepath) as metadata_file:
        self.module_metadata = json.load(metadata_file)
    except FileNotFoundError:
      pass

    if module_template:
      self.module_bazelfile_template = pathlib.Path(module_template)

      if not self.module_bazelfile_template.exists():
        raise RuntimeError(f'Module template file does not exist: {module_template}')
    elif not self.module_bazelfile_template.exists():
      self.module_bazelfile_template = pathlib.Path('/opt/gitlab-ci/data/bazel-module.template.bazel')

  def create_version(self, version: str, url: str, strip_prefix: str|None = None):
    version_path = self.module_path / version

    if version_path.exists():
      raise RuntimeError(f'Version {version} already exists for module {self.name}')

    with requests.get(url, stream=True) as response:
      response.raise_for_status()
      with tempfile.NamedTemporaryFile(mode='w+b',  delete=True, delete_on_close=False) as download_file:
          for chunk in response.iter_content(chunk_size=1024):
              if chunk:
                  download_file.write(chunk)
          download_file.close()

          integrity = utils.sha256_checksum(download_file.name)
          integrity = f'sha256-{integrity}'

    version_path.mkdir(parents=True)

    version_source_contents = {
       'url': url,
       'integrity': integrity,
    }

    if strip_prefix:
      version_source_contents['strip_prefix'] = strip_prefix

    with open(version_path / 'source.json', 'w') as source_file:
      json.dump(version_source_contents, source_file, indent=4)

    self.module_metadata['versions'] = self.module_metadata.get('versions', []) + [version]

    with open(self.module_path / 'metadata.json', 'w') as metadata_file:
      json.dump(self.module_metadata, metadata_file, indent=4)

    with open(self.module_bazelfile_template, 'r') as template_file:
      version_module_file_contents = template_file.read()
      version_module_file_contents = version_module_file_contents.replace('BAZEL_MODULE_NAME', self.name)
      version_module_file_contents = version_module_file_contents.replace('BAZEL_MODULE_VERSION', version)

      with open(version_path / 'MODULE.bazel', 'w') as module_file:
        module_file.write(version_module_file_contents)

    return version_path

