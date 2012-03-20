#include "Python.h"

#ifdef ANDROID
#include <sys/utsname.h>
#include <string.h>
char XPLATFORM[20]; // taken as base linux-armv7l-2.6

const char *
Py_GetPlatform(void)
{
    if (XPLATFORM[0]!=0)
	return XPLATFORM;

    struct utsname u;
    int i;
    if ( uname(&u) < 0 )
	return "unknown";

    strcat (XPLATFORM, u.sysname);
    strcat (XPLATFORM, "-");
    strcat (XPLATFORM, u.machine);
    for (i=0; XPLATFORM[i]; i++)
	XPLATFORM[i]=tolower(XPLATFORM[i]);
    return XPLATFORM;
}
#else

#ifndef PLATFORM
#define PLATFORM "unknown"
#endif

const char *
Py_GetPlatform(void)
{
	return PLATFORM;
}
#endif
