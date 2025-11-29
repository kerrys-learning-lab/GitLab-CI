
class EnforcerFactory:
   MAPPING = {
   }

   @staticmethod
   def create(typeName, title, **kwargs):
      return EnforcerFactory.MAPPING[typeName](title, **kwargs)

