project('pulseaudio-equalizer-ladspa',
    version: '2.7.2',
    meson_version: '>= 0.46.0'
)

pymod = import('python')
python = pymod.find_installation(get_option('python'))
python_major_ver = python.language_version()[0]

modname = 'pulseeq'
appid = 'com.github.pulseaudio-equalizer-ladspa.Equalizer'

prefix = get_option('prefix')
bindir = get_option('bindir')
datadir = get_option('datadir')
pythondir = python.get_path('purelib')

pkgdatadir = join_paths(datadir, meson.project_name())
appdir = join_paths(pythondir, modname)

purelib_option = get_option('purelib')

if not (purelib_option == '')
    purelib_path = purelib_option
else
    purelib_path = python.get_install_dir()
endif

subdir('bin')
subdir('data')
subdir(modname)

