constants_conf = configuration_data()
constants_conf.set('pkgdatadir', join_paths(prefix, pkgdatadir))

constants_file = configure_file(
    input: 'constants.py.in',
    output: 'constants.py',
    configuration: constants_conf,
)

equalizer_sources = ['equalizer.py', constants_file]

python.install_sources(equalizer_sources,
  subdir: modname
)

