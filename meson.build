project('pulseaudio-equalizer',
    version: '2.7.1',
    meson_version: '>= 0.46.0'
)

pymod = import('python')
python = pymod.find_installation()

prefix = get_option('prefix')
bindir = get_option('bindir')
datadir = get_option('datadir')
pythondir = python.get_path('purelib')

pkgdatadir = join_paths(datadir, meson.project_name())
appdir = join_paths(pythondir, meson.project_name())

subdir('bin')
subdir('data')
subdir('equalizer')
