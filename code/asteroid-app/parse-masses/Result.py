# I always hated Either's name, so changed to Result becuase I like Folktale's better.
from pymonad.Monad import *
from pydash import map_, some, filter_, head, every

class Result(Monad):
	""" 
	Represents a calculation that may either fail or succeed.
	An alternative to using exceptions. 'Result' is an abstract type and should not
	be instantiated directly. Instead use 'Ok' (or its alias 'Ok') and 
	'Error' (or its alias 'Error')
	"""

	def __init__(self, value):
		""" Raises a 'NotImplementedError'.  Use 'Ok' or 'Error' instead. """
		raise NotImplementedError

	def __eq__(self, other):
		if not isinstance(other, Result): raise TypeError("Can't compare different types.")

	@classmethod
	def unit(cls, value):
		return Ok(value)

	@classmethod
	def try_(cls, function):
		try:
			result = function()
			return Ok(result)
		except Exception as e:
			return Error(e)

	@classmethod
	def all(cls, *args):
		try:
			dem_args = list(args)
			if some(dem_args, lambda result: isinstance(result, Error)):
				return head(filter_(dem_args, lambda result: isinstance(result, Error)))

			if every(dem_args, lambda result: isinstance(result, Ok) == False):
				return Error(Exception('Some items passed in were not a Result.'))
			
			return Ok(map_(dem_args, lambda result: result.getValue()))
		except Exception as e:
			return Error(e)


class Error(Result):
	""" 
	Represents a calculation which has failed and contains an error code or message. 
	To help with readaility you may alternatively use the alias 'Error'.
	"""

	def __init__(self, errorMsg):
		""" 
		Creates an 'Error' "calculation failed" object.
		'errorMsg' can be anything which gives information about what when wrong.
		"""
		super(Result, self).__init__(errorMsg)

	def __eq__(self, other):
		super(Error, self).__eq__(other)
		if not isinstance(other, Error): return False
		elif (self.getValue() == other.getValue()): return True
		else: return False

	def __ne__(self, other):
		return not self.__eq__(other)

	def __str__(self):
		return "Error: " + str(self.getValue())

	def fmap(self, _): 
		""" Returns the 'Error' instance that was used to call the method. """
		return self

	def amap(self, _):
		""" Returns the 'Error' instance that was used to call the method. """
		return self
		
	def bind(self, _):
		""" Returns the 'Error' instance that was used to call the method. """
		return self

	def match(self, matcher):
		return matcher[Error](self.getValue())

	def get_or_else(self, defaultValue):
		return defaultValue

class Ok(Result):
	""" 
	Represents a calculation which has succeeded and contains the result of that calculation.
	To help with readaility you may alternatively use the alias 'Result'.
	"""

	def __init__(self, value):
		"""
		Creates a 'Ok' "calculation succeeded" object.
		'value' is the actual calculated value of whatever operation was being performed
		and can be any type.
		"""
		super(Result, self).__init__(value)

	def __eq__(self, other):
		super(Ok, self).__eq__(other)
		if not isinstance(other, Ok): return False
		elif (self.getValue() == other.getValue()): return True
		else: return False

	def __ne__(self, other):
		return not self.__eq__(other)

	def __str__(self):
		return "Ok: " + str(self.getValue())

	def fmap(self, function):
		""" 
		Applies 'function' to the contents of the 'Ok' instance and returns a 
		new 'Ok' object containing the result. 
		'function' should accept a single "normal" (non-monad) argument and return
		a non-monad result.
		"""
		return Ok(function(self.getValue()))

	def amap(self, functorValue):
		""" Applies the function stored in the functor to 'functorValue' returning a new Result value. """
		return self.getValue() * functorValue

	def bind(self, function):
		"""
		Applies 'function' to the result of a previous calculation.
		'function' should accept a single "normal" (non-monad) argument and return
		either a 'Error' or 'Ok' type object.
		"""
		return function(self.getValue())

	def match(self, matcher):
		return matcher[Ok](self.getValue())

	def get_or_else(self, defaultValue):
		return self.getValue()

