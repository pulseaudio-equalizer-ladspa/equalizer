project('pulseaudio-equalizer-ladspa',
    version: '2.7.2',
    meson_version: '>= 0.46.0'
)

pymod = import('python')
python = pymod.find_installation()

modname = 'pulseeq'
appid = 'com.github.pulseaudio-equalizer-ladspa.Equalizer'

prefix = get_option('prefix')
bindir = get_option('bindir')
datadir = get_option('datadir')
pythondir = python.get_path('purelib')

pkgdatadir = join_paths(datadir, meson.project_name())
appdir = join_paths(pythondir, modname)

subdir('bin')
subdir('data')
subdir(modname)

