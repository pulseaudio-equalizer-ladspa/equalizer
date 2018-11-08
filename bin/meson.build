bin_conf = configuration_data()
bin_conf.set('appid', appid)
bin_conf.set('pkgdatadir', join_paths(prefix, pkgdatadir))
bin_conf.set('python_major_ver', python_major_ver)
bin_conf.set('purelib_path', join_paths(prefix, purelib_path))

configure_file(
    input: 'pulseaudio-equalizer-gtk.in',
    output: 'pulseaudio-equalizer-gtk',
    configuration: bin_conf,
    install: true,
    install_dir: bindir,
)

configure_file(
    input: 'pulseaudio-equalizer.in',
    output: 'pulseaudio-equalizer',
    configuration: bin_conf,
    install: true,
    install_dir: bindir,
)

