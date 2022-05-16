def Settings( **kwargs ):
  return {
    'flags': [ '-x', 'c++', '-shared', '-o', 'lol', '-lLLVM-13', '-fPIC', '-g'],
  }
