# Maintainer: FFY00 <filipe.lains@gmail.com>
pkgname=pulseaudio-equalizer-ladspa
pkgver=1.0.r0.4856f57
pkgrel=3
pkgdesc="A 15-band equalizer for PulseAudio"
arch=(any)
url="https://github.com/larmedina75/pulseaudio-equalizer-ladspa"
license=('GPL3')
depends=('python-gobject' 'gtk3' 'swh-plugins' 'pulseaudio' 'bc')
makedepends=('git')
provides=('pulseaudio-equalizer-ladspa')
conflicts=('pulseaudio-equalizer-ladspa')
replaces=('pulseaudio-equalizer-ladspa')
source=('remote::git+https://github.com/larmedina75/pulseaudio-equalizer-ladspa')
md5sums=('SKIP')

pkgver() {
  cd "$srcdir/remote"
  git describe --long --tags | sed 's/^v//;s/\([^-]*-\)g/r\1/;s/-/./g;s/\.rc./rc/g'
}

package() {
  install -Dm644 "$srcdir/equalizerrc" "$pkgdir/usr/equalizerrc"

  cp -r "$srcdir/share" "$pkgdir/usr/"
  cp -r "$srcdir/bin" "$pkgdir/usr/"
}
