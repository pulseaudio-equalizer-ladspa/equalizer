constants_conf = configuration_data()
constants_conf.set('pkgdatadir', join_paths(prefix, pkgdatadir))

constants_file = configure_file(
    input: 'constants.py.in',
    output: 'constants.py',
    configuration: constants_conf,
)

equalizer_sources = ['equalizer.py', constants_file]

purelib_path = get_option('purelib')

if not (purelib_path == '')
    install_data(equalizer_sources,
        install_dir: join_paths(purelib_path, modname)
    )
else
    python.install_sources(equalizer_sources,
        subdir: modname
    )
endif
