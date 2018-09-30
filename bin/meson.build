bin_conf = configuration_data()
bin_conf.set('pkgdatadir', join_paths(prefix, pkgdatadir))

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
