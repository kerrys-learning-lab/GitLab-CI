import gitlab.v4.objects
import logging
from .base import Enforcer, CompositeEnforcer
from .factory import EnforcerFactory
from .results import EnforcementResults, Status

LOGGER = logging.getLogger('gitlabci.project')

class AccessLevelEnforcer(CompositeEnforcer):
  def __init__(self, title, **kwargs):
    super().__init__(title, **kwargs)
    self.key = kwargs['key']

  def enforce(self, entity, **kwargs) ->  EnforcementResults:
    LOGGER.debug(f'{self.title} ({self.__class__.__name__}) [{self.key}]')
    value = self._getAttributeFromEntity(self.key, entity)

    result = self._createEnforcementResults(**kwargs)

    enforcedLength = self.value.get('len')
    if enforcedLength and enforcedLength != len(value):
      result += self._createEnforcementResults(status=Status.FAILURE,
                                               msg=f'Should be length {enforcedLength} (actual: {len(entity)})',
                                               **kwargs)

    for v in value:
      result += super().enforce(v, **kwargs).children

    return result

class KeyedCompositeEnforcer(Enforcer):

  def __init__(self, title, **kwargs):
    super().__init__(title, **kwargs)
    LOGGER.debug(f'{self.title} ({self.__class__.__name__})')
    self.enforcers = {}
    self.todo = []

  def __iadd__(self, key):
    LOGGER.debug(f'{self.title} ({self.__class__.__name__}) adding CompositeEnforcer for {key}')
    self.enforcers[key] = CompositeEnforcer(key, **self.kwargs)
    self.todo.append(key)

    return self

  def enforce(self, entity, **kwargs):
    key = kwargs['key']
    subject = kwargs.get('subject', key)

    if key in self.enforcers:
      self.todo.remove(key)
      return self.enforcers[key].enforce(entity, **kwargs)
    else:
      if kwargs.get('fix'):
        entity.delete()
        return self._createEnforcementResults(status=Status.FIX,
                                              msg=f'{subject} removed from Protected Branches',
                                              **kwargs)
      else:
        return self._createEnforcementResults(status=Status.FAILURE,
                                              msg=f'{subject} is unexpected',
                                              **kwargs)

class ProtectedBranchEnforcer(KeyedCompositeEnforcer):

  def __init__(self, title, **kwargs):
    super().__init__(title, **kwargs)

    self.strict = self.value.get('strict', True)

    for r in self.value.get('required', []):
      self += r.replace('{project-path}', self.project.path)

  def enforce(self, entity: gitlab.v4.objects.Project, **kwargs) ->  EnforcementResults:
    results = self._createEnforcementResults(**kwargs)

    for branch in entity.protectedbranches.list(iterator=True):
      kwargs['subject'] = f'Protected branch: \'{branch.name}\''
      kwargs['key'] = branch.name
      thisResult = super().enforce(branch, **kwargs)
      if thisResult is not None and thisResult.status == Status.FAILURE and kwargs.get('fix'):
        # Easiest way (and DRY) is to delete the incorrect branc protections
        # and recreate in postEnforce
        branch.delete()
        self.todo.append(branch.name)
        thisResult = None
      results += thisResult

    return results

  def postEnforce(self, entity, **kwargs) ->  EnforcementResults:
    LOGGER.debug(f'{self.title} ({self.__class__.__name__}) - postEnforce')
    if self.todo:
      results = self._createEnforcementResults(status=Status.FIX if kwargs.get('fix') else Status.FAILURE)

      if kwargs.get('fix'):
        for t in self.todo:
          newProtectedBranch = { 'name': t}
          for childEnforcer in self.enforcers[t].enforcers.values():
            key = childEnforcer.kwargs.get('alt', childEnforcer.key)
            if hasattr(childEnforcer, 'enforcers'):
              arrayValue = []
              for cc in childEnforcer.enforcers.values():
                arrayValue.append({cc.key: cc.value})
              newProtectedBranch[key] = arrayValue
            else:
              newProtectedBranch[key] = childEnforcer.value
          entity.protectedbranches.create(newProtectedBranch)
          results += self._createEnforcementResults(status=Status.FIX,
                                                    msg=f'Updated protections for branch \'{t}\'',
                                                    **kwargs)

      else:
        for t in self.todo:
          results += self._createEnforcementResults(status=Status.FAILURE,
                                                    msg=f'Expected \'{t}\' to be protected',
                                                    **kwargs)
      return results

class SettingsEnforcer(CompositeEnforcer):

  def __init__(self, title, **kwargs):
    super().__init__(title, **kwargs)

EnforcerFactory.MAPPING['protected-branches'] = ProtectedBranchEnforcer
EnforcerFactory.MAPPING['access-level'] = AccessLevelEnforcer
EnforcerFactory.MAPPING['project-settings'] = SettingsEnforcer
