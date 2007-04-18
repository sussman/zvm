#include <stdio.h>
#include <stdlib.h>
#include "glk.h"
#include "cheapglk.h"

int gli_screenwidth = 80;
int gli_screenheight = 24; 
int gli_utf8output = FALSE;
int gli_utf8input = FALSE;

static int inittime = FALSE;
