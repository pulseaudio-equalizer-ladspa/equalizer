# Maintainer: FFY00 <filipe.lains@gmail.com>
pkgname=pulseaudio-equalizer-ladspa-ffy00-git
pkgver=1.0.r0.4856f57
pkgrel=3
pkgdesc="A 15-band equalizer for PulseAudio (FFY00's fork)"
arch=(any)
url="https://github.com/pulseaudio-equalizer-ladspa"
license=('GPL3')
depends=('python-gobject' 'gtk3' 'swh-plugins' 'pulseaudio' 'bc')
makedepends=('git')
optdepends=('python2-gobject: python2 support')
provides=('pulseaudio-equalizer-ladspa')
conflicts=('pulseaudio-equalizer-ladspa')
replaces=('pulseaudio-equalizer-ladspa')
source=('git+https://github.com/pulseaudio-equalizer-ladspa/equalizer')
md5sums=('SKIP')

pkgver() {
  cd equalizer
  git describe --long --tags | sed 's/^v//;s/\([^-]*-\)g/r\1/;s/-/./g;s/\.rc./rc/g'
}

build() {
  rm -rf build
  arch-meson equalizer build
  ninja -C build
}

package() {
  DESTDIR="$pkgdir" meson install -C build

  python -m compileall -d /usr/lib "$pkgdir/usr/lib"
  python -O -m compileall -d /usr/lib "$pkgdir/usr/lib"
}
