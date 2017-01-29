# pulseaudio-equalizer
Getting serious about sound output and pulseaudio (fetched stuff from launchpad)
A LADSPA based multiband equalizer approach for getting better sound out of pulseaudio. This equalizer clearly is more potent than the (deprecated ?), optional one from Pulseaudio.


The files are from 
https://code.launchpad.net/~psyke83/+junk/pulseaudio-equalizer
https://github.com/jjo/config/tree/master/.pulse

The end-result was supposed to be:
http://www.webupd8.org/2013/10/system-wide-pulseaudio-equalizer.html

https://aur.archlinux.org/packages/pulseaudio-equalizer-ladspa/


Much thanks to kabili207 gtk+ 3 and python 3 are now supported:

"Support for both was added by using pygtkcompat. Minimal changes
were required to allow this.

The source code was also run through a formatter to correct the
heavy mix of tabs and spaces. I have no idea how it even ran with
such inconsistent indentation."

In version 4.0 the following was fixed: the involuntary volume raise issue,
volume detection and implementation of --color=never for grep.

Thanks again to kabili207 :)
