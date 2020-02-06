from os.path import basename, join
import inspect
from fileinput import FileInput
import re

Import('env')

# it is possible to override any of defines from mbed_config.h
mbed_config_overrides =	{
  "MBED_CONF_NEWLIB_PARAM": 2
}

# full path to mbed_config.h
mbed_config = join(env.subst("$BUILD_DIR"), "mbed_config.h")

# just some default values
width_param = width_val = 1

# we will see the name of pio environment and this script name as the cause of overridding
env_script_name = env['PIOENV'] + ':' + basename(inspect.getfile(inspect.currentframe()))

# loop throug each line of file
for line in FileInput(mbed_config, inplace=True):
    line = line.rstrip('\r\n')
    newline = None
    for key in mbed_config_overrides.keys():
        if line.startswith("#define"):
            # if widths still have default values
            if width_param == 1 or width_val == 1:
                # split string into columns
                columns = []
                # column may have characters from a to Z, digits from 0-9, the underscore _ character
                # or # or / or : or |
                for x in re.finditer('(\w|#|/|:|\|)+', line):
                    columns.append(x.start())
                if (len(columns) >= 4):
                    # decrease by 1 as format string has one whitespace
                    # in case if widths will not be set
                    width_param = columns[2] - columns[1] - 1
                    width_val = columns[3] - columns[2] - 1

        # parameter redefinition
        if key in line:
            newline = '#define {:{wp}} {:{wv}} // set by {}'.format(key, str(mbed_config_overrides[key]),
                        env_script_name, wp=width_param, wv=width_val)

    # write processed or original line back into file
    print(newline or line)
