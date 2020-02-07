from os.path import basename, join
import inspect

Import('env')

#
# add undef for each define in header file
#
def parse_mbed_config_override_h(fname):
    content = []
    try:
        with open(fname) as f:
            lines = f.readlines()
            for line in lines:
                # looking for lines with #define
                if line.startswith('#define'):
                    # add #undef for found define
                    content.append('#undef ' + line.split()[1] + '\n')
            # add original file content after all #undef
            content.extend(lines)
            content.append('\n')
    except:
        pass
    
    return content


#
# process mbed_config.h and add all defines found in overrides
#
def process(overrides):
    # full path to mbed_config.h
    mbed_config = join(env.subst('$BUILD_DIR'), 'mbed_config.h')

    content = []
    try:
        with open(mbed_config) as f:
            content = f.readlines()
    except:
        pass

    if len(content):
        # go up from end to look for #endif
        i = len(content) - 1
        while (i and not content[i].startswith('#endif')):
            i -= 1

        # stick to #endif line
        i -= len(content)
        # insert all overrides
        content[i:i] = '// platformio.ini:' + basename(inspect.getfile(inspect.currentframe())) + '\n'
        content[i:i] = overrides

        with open(mbed_config, "w") as f:
            f.writelines(content)

# list for overrides
mbed_config_overrides =	[]

# path for header files
base_path = join(env['PROJECT_DIR'], 'tools')
# base filename for header files
base_name = 'mbed_config_override'

# extract defines from file for all boards
common_h = join(base_path, base_name + '.h')
mbed_config_overrides.extend(parse_mbed_config_override_h(common_h))

# extract defines from file for project's board
board_h = join(base_path, base_name + '_' + env.BoardConfig().id + '.h')
mbed_config_overrides.extend(parse_mbed_config_override_h(board_h))

# process overrides if we have defines for that
if (len(mbed_config_overrides)):
    process(mbed_config_overrides)
