#include "mbed.h"

#define VALUE_TO_STRING(x) #x
#define VALUE(x) VALUE_TO_STRING(x)
#define VAR_NAME_VALUE(var) #var " = "  VALUE(var)

#pragma message(VAR_NAME_VALUE(MBED_CONF_NEWLIB_PARAM))

int main()
{
}
