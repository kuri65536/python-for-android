#include "Python.h"

#ifdef ANDROID
#include <sys/utsname.h>
#include <string.h>
char PLATFORM[20]={0}; // taken as base linux-armv7l-2.6

const char *
Py_GetPlatform(void)
{
    if (PLATFORM[0]!=0)
	return PLATFORM;

    struct utsname u;
    int i;
    if ( uname(&u) < 0 )
	return "unknown";

    strcat (PLATFORM, u.sysname);
    strcat (PLATFORM, "-");
    strcat (PLATFORM, u.machine);
    for (i=0; PLATFORM[i]; i++)
	PLATFORM[i]=tolower(PLATFORM[i]);
    return PLATFORM;
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
