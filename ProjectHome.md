Back before computers had decent graphics, people wrote adventure games that were purely based in textual conversation. It was sort of like a choose-your-own-adventure book: you move around to different locations, receiving descriptions of what you can see and interact with, solving puzzles, and so on.  The interactive fiction community has a [good introduction](http://www.ifwiki.org/index.php/FAQ) to the genre. It's somewhere between game and a work of fiction. If the writing and characters are good enough, some games approach 'novel' status; but it's the interactivity that makes it exciting.

The original company which sold text adventures on store shelves in the 1980's (Infocom) actually designed a virtual machine for their games to run on. Much like Java, all they had to do was port their "z-machine" emulator once to each platform (C64, PET, TRS-80, Apple II, IBM, etc.) Then their compiler would produce bytecode runnable on each computer.

In the late 90's, long after Infocom perished, the z-machine was rediscovered by a community of internet enthusiasts. New z-machine emulators were written for Windows, Mac, Linux, various PDAs (or even Emacs!)

This project is an attempt to write a portable z-machine emulator in Python, to be re-used in different applications.

Project Goals:

  * **Portability**. ZVM is written exclusively in the Python programming language, as an importable code module.

  * **Abstracted user interface**. ZVM implements only the z-machine. It is meant to be used as the backend in other programs that provide a user interface by sending all I/O calls through the [GLK API](http://www.eblong.com/zarf/glk/).

  * **Compatibility**. ZVM will implement a Z-Machine architecture according to the [official specification](http://www.inform-fiction.org/zmachine).  It will also support the [Blorb](http://www.eblong.com/zarf/blorb/blorb.html) game resource format (since that's what [Inform 7](http://www.inform-fiction.org/I7/Inform%207.html) now outputs by default), as well as the standard [Quetzal](http://www.ifarchive.org/if-archive/infocom/interpreters/specification/savefile_14.txt) save-file format.

  * **Coverage**. Over the years, the Z-machine architecture was revised and refined: 8 versions are known to exist. ZVM initially aims to support Z-machine versions 1 through 5, and will eventually support 7 and 8 as well.

  * **Readability**. It's easy to implement an emulator with "clever" code that looks like line noise... we've seen a few!   We've broken the z-machine's components of the machine into clean, [well-documented classes](http://code.google.com/p/zvm/wiki/ZvmDesign). Readability is key, since speed isn't going to be an issue when emulating a 30-year old VM on a modern computer.


Status:

As of July 2008, we're able to execute the first few bits of 'curses.z5'.  That is, the opening quotation prints on the screen.  As we attempt to execute this story, we're implementing each opcode as we encounter them.  :-)