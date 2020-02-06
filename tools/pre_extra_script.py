Import('env')

env.Append(CPPDEFINES=[
  ("MBED_CONF_NEWLIB_PARAM", 2)
])
