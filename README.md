# pulseaudio-equalizer
Getting serious about sound output and pulseaudio (fetched stuff from launchpad)
A LADSPA based multiband equalizer approach for getting better sound out of pulseaudio. This equalizer clearly is more potent than the (deprecated ?), optional one from Pulseaudio.


The files are from 
https://code.launchpad.net/~psyke83/+junk/pulseaudio-equalizer
https://github.com/jjo/config/tree/master/.pulse

The end-result was supposed to be:
http://www.webupd8.org/2013/10/system-wide-pulseaudio-equalizer.html

https://aur.archlinux.org/packages/pulseaudio-equalizer-ladspa/

Since development has stalled, the GUI isn't launching and the locally created config-files are getting messed up (the options appear twice) - equalizerrc, equalizerrc.availablepresets - even when forcing python via

export EPYTHON=python2.7

it still errors out ...


Currently I'm enabling it via

pulseaudio-equalizer toggle

and

having a pre-set preset option in pulseaudio-equalizer
(e.g. PA_CURRENT_PRESET="Club.preset")