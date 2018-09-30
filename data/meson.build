install_subdir('presets', install_dir: pkgdatadir)

install_data(appid + '.desktop',
    install_dir: join_paths(datadir, 'applications'),
)

gnome = import('gnome')

# Compiling the resources
gnome.compile_resources(
  appid,
  appid + '.gresource.xml',
  gresource_bundle: true,
  source_dir: meson.current_build_dir(),
  install_dir: pkgdatadir,
  install: true
)
