import enum
import git
import logging
import re

from ..info import Info
from .model import PipelineVersion

LOGGER = logging.getLogger('gitlabci.version')


# ----------------------------------------------------------------------------
class InvalidSemanticVersionError(RuntimeError):
    ''' Raised when a tag does not comply with the expected semantic
        version requirements '''


# ----------------------------------------------------------------------------
class CantDeduceVersionTypeError(RuntimeError):
    ''' Raised when the factory cannot deduce the version information from
        the given pipeline information '''


# ----------------------------------------------------------------------------
class VersionType(enum.StrEnum):
    CM_TAG = 'tag'
    DEFAULT_BRANCH = 'default-branch'
    CM_BRANCH = 'cm-branch'
    ANY_REF = 'any-branch'


# ----------------------------------------------------------------------------
class Languages(enum.StrEnum):
    PYTHON = 'python'
    PHP = 'php'


# Release branches contain only major.minor (patch is applied for tags)
# Examples:
#   - 2.0
#   - foo-bar-3.1
RELEASE_BRANCH_RE = re.compile(r'^(?P<prefix>[^\d]+)-(?P<major>\d+)\.(?P<minor>\d+)$')

RELEASE_TAG_RE=re.compile(r'^(?P<prefix>[^\d]+)?(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)$')


class VersionInfo:

    def __init__(self, info: Info, ref: str, versionType: VersionType, **kwargs):
        self.pipelineInfo = info
        self.commitRef = ref
        self.versionType = versionType
        self.config = kwargs
        self.version = ref
        self._semantic = None

        # Check if the version/tag begins with a single 'v'
        vMatch = re.search(r'^v\d+.*', self.version)
        if vMatch:
            self.version = self.version[1:]

    @property
    def major(self):
        try:
            return self.config['major']
        except KeyError:
            raise InvalidSemanticVersionError()

    @property
    def minor(self):
        try:
            return self.config['minor']
        except KeyError:
            raise InvalidSemanticVersionError()

    @property
    def patch(self):
        try:
            return self.config['patch']
        except KeyError:
            raise InvalidSemanticVersionError()

    @property
    def defaultSemverPrefix(self):
        return self.config.get('PROJECT_SEMVER_PREFIX',
                               self.config.get('DEFAULT_SEMVER_PREFIX',
                                               '0.0.0'))

    @property
    def semantic(self) -> str:
        if not self._semantic:
            match self.versionType:
                case VersionType.CM_TAG:
                    return f'{self.major}.{self.minor}.{self.patch}'
                case VersionType.CM_BRANCH:
                    return f'{self.major}.{self.minor}.{self.patch}-rc+{self.pipelineInfo.pipelineIid}'
                case VersionType.DEFAULT_BRANCH:
                    return f'{self.defaultSemverPrefix}-{self.pipelineInfo.commitBranch}+{self.pipelineInfo.pipelineIid}'
                case VersionType.ANY_REF:
                    return f'{self.defaultSemverPrefix}-{self.pipelineInfo.commitRefSlug}+{self.pipelineInfo.pipelineIid}'

            raise InvalidSemanticVersionError()

        return self._semantic

    def lang(self, lang: Languages):
        if self.versionType == VersionType.CM_TAG:
                return self.semantic

        match lang:
            case Languages.PYTHON:
                match self.versionType:
                    case VersionType.CM_BRANCH:
                        return f'{self.major}.{self.minor}.{self.patch}+rc.{self.pipelineInfo.pipelineIid}'
                    case VersionType.DEFAULT_BRANCH:
                        return f'{self.defaultSemverPrefix}+{self.pipelineInfo.commitBranch}.{self.pipelineInfo.pipelineIid}'
                    case VersionType.ANY_REF:
                        return f'{self.defaultSemverPrefix}+{self.pipelineInfo.commitRefSlug}.{self.pipelineInfo.pipelineIid}'
            case Languages.PHP:
                match self.versionType:
                    case VersionType.CM_BRANCH:
                        return f'dev-{self.major}.{self.minor}.{self.patch}-rc+{self.pipelineInfo.pipelineIid}'
                    case VersionType.DEFAULT_BRANCH:
                        return f'dev-{self.defaultSemverPrefix}-{self.pipelineInfo.commitBranch}+{self.pipelineInfo.pipelineIid}'
                    case VersionType.ANY_REF:
                        return f'dev-{self.defaultSemverPrefix}-{self.pipelineInfo.commitRefSlug}+{self.pipelineInfo.pipelineIid}'

# ----------------------------------------------------------------------------
class VersionFactory:

    INIT_TYPES = [
        ('commitBranch',    '_initFromBranch'),
        ('commitTag',       '_initFromTag'),
        ('default',         '_initDefault'),
    ]

    def __init__(self, info: Info | None = None, **kwargs):
        self.info = info or Info.create()
        self.config = kwargs

    @staticmethod
    def create(info: Info | None = None, **kwargs) -> PipelineVersion:
        info = info or Info.create()
        LOGGER.error(info)
        versionInfo = VersionFactory._inferVersionInfoFromPipeline(info, **kwargs)

        pipelineVersion = PipelineVersion(version=versionInfo.version,
                                          semanticVersion=versionInfo.semantic,
                                          langPythonVersion=versionInfo.lang(Languages.PYTHON),
                                          langPhpVersion=versionInfo.lang(Languages.PHP))

        LOGGER.info(f'Calculated version: \'{pipelineVersion.version}\', semanticVersion: \'{pipelineVersion.semanticVersion}\'')
        LOGGER.debug(f'    Python version: {pipelineVersion.langPythonVersion}')
        LOGGER.debug(f'    PHP version: {pipelineVersion.langPhpVersion}')

        return pipelineVersion

    @staticmethod
    def _inferVersionInfoFromPipeline(info: Info, **kwargs) -> VersionInfo:
        for initTypeName, initTypeFunc in VersionFactory.INIT_TYPES:

            try:
                varValue = getattr(info, initTypeName, None)
                if initTypeName == 'default' or varValue is not None:
                    LOGGER.error(f'Calling {initTypeName} ({initTypeFunc})')
                    func = getattr(VersionFactory, initTypeFunc)
                    return func(info, **kwargs)
            except CantDeduceVersionTypeError as ex:
                LOGGER.error(ex)
                pass

        raise CantDeduceVersionTypeError()

    @staticmethod
    def _initFromBranch(info: Info, **kwargs) -> VersionInfo:
        LOGGER.error(info.commitBranch)
        assert(info.commitBranch)
        if info.commitBranch == info.defaultBranch:
            LOGGER.debug(f'Creating version from default branch: {info.commitBranch}')

            return VersionInfo(info,
                               info.commitBranch,
                               VersionType.DEFAULT_BRANCH,
                               **kwargs)

        reMatch = RELEASE_BRANCH_RE.match(info.commitBranch)

        if not reMatch or not isinstance(info.projectDir, git.Repo):
            # If not a CM branch, use the default pipeline _baseVersion calculation
            raise CantDeduceVersionTypeError()

        LOGGER.debug(f'Creating version from protected branch: {info.commitBranch}')
        major = reMatch.group('major')
        minor = reMatch.group('minor')

        nextPatchLevel = VersionFactory._inferNextPatchLevel(info, **kwargs)

        return VersionInfo(info,
                           info.commitBranch,
                           VersionType.CM_BRANCH,
                           major=major,
                           minor=minor,
                           patch=nextPatchLevel,
                           **kwargs)

    @staticmethod
    def _initFromTag(info: Info, **kwargs) -> VersionInfo:
        assert(info.commitTag)
        reMatch = RELEASE_TAG_RE.match(info.commitTag)
        if not reMatch:
            raise InvalidSemanticVersionError(f'Expected a semantic version.  Got: \'{info.commitTag}\'')

        LOGGER.debug(f'Creating version from protected tag: {info.commitTag}')

        return VersionInfo(info,
                           info.commitTag,
                           VersionType.CM_TAG,
                           major=reMatch.group('major'),
                           minor=reMatch.group('minor'),
                           patch=reMatch.group('patch'),
                           **kwargs)

    @staticmethod
    def _initDefault(info: Info, **kwargs) -> VersionInfo:
        LOGGER.debug(f'Creating version from slug: {info.commitRefSlug}')

        return VersionInfo(info,
                           info.commitRefSlug,
                           VersionType.ANY_REF,
                           **kwargs)

    @staticmethod
    def _inferNextPatchLevel(info: Info, **kwargs):
        if not isinstance(info.projectDir, git.Repo):
            # If not a CM branch, use the default pipeline _baseVersion calculation
            raise CantDeduceVersionTypeError()

        nextPatchLevel = 0
        matchingTags = info.projectDir.git.tag('-l', 'v*').split()
        for tag in matchingTags:
            reMatch = RELEASE_TAG_RE.match(tag)
            if reMatch:
                tagPatchLevel = int(reMatch.group('patch'))
                if tagPatchLevel >= nextPatchLevel:
                    LOGGER.debug(f'Skipping patch level {nextPatchLevel} (superseded)')
                    nextPatchLevel = tagPatchLevel + 1

        return nextPatchLevel
