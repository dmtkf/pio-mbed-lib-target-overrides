from os.path import basename, join
import inspect
from fileinput import FileInput
import re

Import('env')

# dictionary for overrides
mbed_config_overrides =	{
}

#
# extract defines from header file
#
def parse_mbed_config_override_h(fname):
    defines = {}
    try:
        with open(fname) as f:
            for line in f:
                if line.startswith('#define'):
                    # split string into columns
                    columns = []
                    # column may have characters from a to Z, digits from 0-9, the underscore _ character
                    # or # or / or : or |
                    for x in re.finditer('(\w|#|/|:|\|)+', line):
                        columns.append(x.group())
                    # add param:value into defines dictionary
                    if (len(columns) >= 3):
                        defines.update({columns[1]: columns[2]})
    except:
        pass
    
    return defines

#
# process mbed_config.h and replace all defines found in overrides
#
def process(overrides):
    # full path to mbed_config.h
    mbed_config = join(env.subst('$BUILD_DIR'), 'mbed_config.h')

    # just some default values
    width_param = width_val = 1

    # we will see the name of pio environment and this script name as the cause of overridding
    env_script_name = env['PIOENV'] + ':' + basename(inspect.getfile(inspect.currentframe()))

    # loop throug each line of file
    for line in FileInput(mbed_config, inplace=True):
        line = line.rstrip('\r\n')
        newline = None
        for key in overrides.keys():
            if line.startswith('#define'):
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

# path for header files
base_path = join(env['PROJECT_DIR'], 'tools')
# base filename for header files
base_name = 'mbed_config_override'

# extract defines from file for all environments
common_h = join(base_path, base_name + '.h')
mbed_config_overrides.update(parse_mbed_config_override_h(common_h))

# extract defines from file for current environment
environment_h = join(base_path, base_name + '_' + env['PIOENV'] + '.h')
mbed_config_overrides.update(parse_mbed_config_override_h(environment_h))

# process overrides if we have defines for that
if (len(mbed_config_overrides)):
    process(mbed_config_overrides)
