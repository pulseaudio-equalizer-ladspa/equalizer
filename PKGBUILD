# Maintainer: FFY00 <filipe.lains@gmail.com>
pkgname=pulseaudio-equalizer-ladspa-ffy00-git
pkgver=1.0.r0.4856f57
pkgrel=1
pkgdesc='A 15-band equalizer for PulseAudio'
arch=(any)
url='https://github.com/pulseaudio-equalizer-ladspa'
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
  mkdir -p equalizer/build
  cd equalizer/build

  arch-meson ..

  ninja
}

package() {
  cd equalizer/build

  DESTDIR="$pkgdir" meson install

  python -m compileall -d /usr/lib "$pkgdir/usr/lib"
  python -O -m compileall -d /usr/lib "$pkgdir/usr/lib"
  
  # It's GLP3 but has a specific copyright string
  install -Dm ../LICENSE "$pkgdir"/usr/share/licenses/$pkgname/LICENSE
}
