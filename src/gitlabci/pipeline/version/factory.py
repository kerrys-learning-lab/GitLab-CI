import logging
import re

from ..info import Info
from .model import PipelineVersion

LOGGER = logging.getLogger('gitlabci.version')

class InvalidSemanticVersion(RuntimeError):
    ''' Raised when a tag does not comply with the expected semantic
        version requirements '''

# Release branches contain only major.minor (patch is applied for tags)
# Examples:
#   - 2.0
#   - foo-bar-3.1
RELEASE_BRANCH_RE = re.compile(r'^([^\d]+)?(?P<majorMinor>\d+\.\d+)$')

RELEASE_TAG_RE=re.compile(r'^([^\d]+)?(?P<semver>\d+\.\d+\.(?P<patch>\d+))$')

class VersionFactory:

    VERSION_TYPES = [
        'commitBranch',
        'commitTag',
    ]

    @staticmethod
    def create(info: Info | None = None, **kwargs) -> PipelineVersion:
        info = info or Info.create()
        for attrName in VersionFactory.VERSION_TYPES:
            varValue = getattr(info, attrName)
            if varValue is not None:
                func = getattr(VersionFactory, f'createPipelineVersionFrom_{attrName}')
                version = func(info, **kwargs)
                if version is not None:
                    return version

        return VersionFactory.createDefaultPipelineVersion(info, **kwargs)

    @staticmethod
    def createPipelineVersionFrom_commitBranch(info: Info, **kwargs) -> PipelineVersion|None:
        assert(info.commitBranch)
        if info.commitBranch == info.defaultBranch:
            LOGGER.debug(f'Creating version from default branch: {info.commitBranch}')
            semverPrefix = kwargs.get('PROJECT_SEMVER_PREFIX',
                                    kwargs.get('DEFAULT_SEMVER_PREFIX', '0.0.0'))
            return VersionFactory._create(VersionFactory.buildVersionString(info.commitBranch,
                                                                            info),
                                          VersionFactory.buildVersionString(semverPrefix,
                                                                            info,
                                                                            prerelease=info.commitBranch,
                                                                            metadata=True),
                                          VersionFactory.buildVersionString(semverPrefix,
                                                                            info,
                                                                            prerelease=info.commitBranch,
                                                                            metadata=True,
                                                                            pythonic=True))

        reMatch = RELEASE_BRANCH_RE.match(info.commitBranch)

        if not info.commitRefProtected or not reMatch:
            # If not a protected branch or it's not a CM branch, use the
            # default pipeline version calculation
            return

        LOGGER.debug(f'Creating version from protected branch: {info.commitBranch}')
        majorMinor = reMatch.group('majorMinor')

        nextPatchLevel = 0
        matchingTags = info.projectDir.git.tag('-l', f'{info.commitBranch}.*').split()
        for tag in matchingTags:
            reMatch = RELEASE_TAG_RE.match(tag)
            if reMatch:
                tagPatchLevel = int(reMatch.group('patch'))
                if tagPatchLevel >= nextPatchLevel:
                    LOGGER.debug(f'Skipping patch level {nextPatchLevel} (superseded)')
                    nextPatchLevel = tagPatchLevel + 1

        return VersionFactory._create(VersionFactory.buildVersionString(f'{info.commitBranch}',
                                                                        info),
                                      VersionFactory.buildVersionString(f'{majorMinor}.{nextPatchLevel}',
                                                                        info,
                                                                        prerelease=True,
                                                                        metadata=True),
                                      VersionFactory.buildVersionString(f'{majorMinor}.{nextPatchLevel}',
                                                                        info,
                                                                        prerelease=True,
                                                                        metadata=True,
                                                                        pythonic=True))

    @staticmethod
    def createPipelineVersionFrom_commitTag(info: Info, **kwargs) -> PipelineVersion:
        assert(info.commitTag)
        reMatch = RELEASE_TAG_RE.match(info.commitTag)
        if not reMatch:
            raise InvalidSemanticVersion(f'Expected a semantic version.  Got: \'{info.commitTag}\'')

        LOGGER.debug(f'Creating version from protected tag: {info.commitTag}')
        return VersionFactory._create(VersionFactory.buildVersionString(info.commitTag,
                                                                        info),
                                      VersionFactory.buildVersionString(reMatch.group('semver'),
                                                                        info),
                                      VersionFactory.buildVersionString(reMatch.group('semver'),
                                                                        info,
                                                                        pythonic=True))

    @staticmethod
    def _create(version: str, semanticVersion: str, pythonicVersion: str) -> PipelineVersion:
        LOGGER.debug(f'Calculated version: \'{version}\', semanticVersion: \'{semanticVersion}\'')
        return PipelineVersion(version=version,
                               semanticVersion=semanticVersion,
                               pythonicVersion=pythonicVersion)

    @staticmethod
    def createDefaultPipelineVersion(info: Info, **kwargs) -> PipelineVersion:
        LOGGER.debug(f'Creating version from slug: {info.commitRefSlug}')
        semverPrefix = kwargs.get('PROJECT_SEMVER_PREFIX',
                                  kwargs.get('DEFAULT_SEMVER_PREFIX', '0.0.0'))

        return VersionFactory._create(VersionFactory.buildVersionString(info.commitRefSlug, info),
                                      VersionFactory.buildVersionString(semverPrefix,
                                                                        info,
                                                                        prerelease=info.commitRefSlug,
                                                                        metadata=True),
                                      VersionFactory.buildVersionString(semverPrefix,
                                                                        info,
                                                                        prerelease=info.commitRefSlug,
                                                                        metadata=True,
                                                                        pythonic=True))

    @staticmethod
    def buildVersionString(version: str,
                           info: Info,
                           prerelease: str|bool|None = None,
                           metadata: str|bool|None = None,
                           pythonic: bool = False):
        version = version.replace(info.projectName, '')
        version = version.strip('-')

        # Check if the version/tag begins with a single 'v'
        vMatch = re.search(r'^v\d+.*', version)
        if vMatch:
            version = version[1:]

        if prerelease:
            prerelease = prerelease if isinstance(prerelease, str) else 'rc'
        if metadata:
            metadata = metadata if isinstance(metadata, str) else info.pipelineIid

        v = version

        if pythonic:
          v = f'{v}+{prerelease}' if prerelease else v
          v = f'{v}.{metadata}' if metadata else v
        else:
          v = f'{v}-{prerelease}' if prerelease else v
          v = f'{v}+{metadata}' if metadata else v

        return v
