import abc
import logging

from .factory import EnforcerFactory
from .results import EnforcementResults, Status

LOGGER = logging.getLogger('gitlabci.project')

class Enforcer:
  def __init__(self, title, **kwargs):
    self.title = title.format(**kwargs)
    self.key = kwargs.get('key')
    self.value = kwargs.get('value')
    self.kwargs = kwargs

  @property
  def project(self):
    try:
      return self.kwargs['project']
    except KeyError:
      raise RuntimeError(f'Unable to complete \'{self.title}\': \'project\' is a required field')

  def _getAttributeFromEntity(self, attrName, entity):
    try:
      return getattr(entity, attrName)
    except AttributeError:
      raise RuntimeError(f'Attribute {attrName} not found in entity {entity}')

  def _createEnforcementResults(self,
                                status: Status = Status.SUCCESS,
                                **kwargs) ->  EnforcementResults:
    return EnforcementResults(self.title,
                              status,
                              **kwargs)

  def enforce(self, entity, **kwargs) ->  EnforcementResults:
    try:
      LOGGER.debug(f'{self.title} ({self.__class__.__name__}) - enforce')
      result = self._wrapEnforceWithFix(entity, **kwargs)
      result += self.postEnforce(entity, **kwargs)
      return result
    except Exception as ex:
      if LOGGER.isEnabledFor(logging.DEBUG):
        LOGGER.exception(ex)
      return self._createEnforcementResults(status=Status.ERROR,
                                            msg=str(ex),
                                            **kwargs)

  def _wrapEnforceWithFix(self, entity, **kwargs) -> EnforcementResults:
      result = self._enforce(entity, **kwargs)
      if result.status == Status.FAILURE and kwargs.get('fix'):
        return self.fix(entity, **kwargs) or result
      else:
        return result

  def postEnforce(self, entity, **kwargs) -> EnforcementResults|None:
    return None

  @abc.abstractmethod
  def _enforce(self, entity, **kwargs) -> EnforcementResults:
    '''  '''

  def fix(self, entity, **kwargs) -> EnforcementResults:
    ''' '''

class CompositeEnforcer(Enforcer):
  def __init__(self, title, **kwargs):
    super().__init__(title, **kwargs)
    self.enforcers = {}
    for key, value in self.kwargs.get('children', {}).items():
      value = kwargs | value
      self.enforcers[key] = EnforcerFactory.create(value.get('type', 'composite'),
                                                   key,
                                                   **value)

  def _enforce(self, entity, **kwargs) ->  EnforcementResults:
    results = self._createEnforcementResults(**kwargs)
    for value in self.enforcers.values():
      thisResult = value.enforce(entity, **kwargs)
      if thisResult is not None and thisResult.status == Status.FAILURE and kwargs.get('fix'):
        results += value.fix(entity, **kwargs) or thisResult
      else:
        results += thisResult

    return results

  def postEnforce(self, entity, **kwargs):
    LOGGER.debug(f'{self.title} ({self.__class__.__name__}) - postEnforce')
    results = self._createEnforcementResults(**kwargs)

    for value in self.enforcers.values():
      results += value.postEnforce(entity, **kwargs)

    if results.children:
      return results

class NestedEnforcer(CompositeEnforcer):

  def __init__(self, title, **kwargs):
    super().__init__(title, **kwargs)

  def _enforce(self, entity, **kwargs):
    entity = getattr(entity, self.key)
    kwargs['subject'] = self.title
    return super()._enforce(entity, **kwargs)

class EntityAttributeEnforcer(Enforcer):
  def __init__(self, title, **kwargs):
    super().__init__(title, **kwargs)

  def _enforce(self, entity, **kwargs) ->  EnforcementResults:
    entityAttrs = getattr(entity, self.key)
    if entityAttrs == self.value:
      return self._createEnforcementResults(**kwargs)
    else:
      return self._createEnforcementResults(status=Status.FAILURE,
                                            msg=f'Should be \'{self.value}\' (actual: {entityAttrs})',
                                            **kwargs)

  def fix(self, entity, **kwargs) -> EnforcementResults:
    LOGGER.info(f'Updating {entity.name} / {self.key}={self.value} for {self.project.name}')
    setattr(entity, self.key, self.value)
    self.project.save()
    return self._createEnforcementResults(status=Status.FIX, **kwargs)

class EntityAttributeKeyValueEnforcer(Enforcer):
  def __init__(self, title, **kwargs):
    super().__init__(title, **kwargs)

  def _enforce(self, entity, **kwargs) ->  EnforcementResults:
    if entity[self.key] == self.value:
      return self._createEnforcementResults(**kwargs)
    else:
      return self._createEnforcementResults(status=Status.FAILURE,
                                            msg=f'Should be \'{self.value}\' (actual: {entity[self.key]})',
                                            **kwargs)


EnforcerFactory.MAPPING['exact-match'] = EntityAttributeEnforcer
EnforcerFactory.MAPPING['composite'] = CompositeEnforcer
EnforcerFactory.MAPPING['key-value'] = EntityAttributeKeyValueEnforcer
EnforcerFactory.MAPPING['nested'] = NestedEnforcer
