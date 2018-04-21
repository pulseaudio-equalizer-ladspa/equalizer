# Maintainer: FFY00 <filipe.lains@gmail.com>
pkgname=pulseaudio-equalizer-ladspa-ffy00-git
pkgver=3.0
pkgrel=1
pkgdesc="A 15-band equalizer for PulseAudio (FFY00 fork)"
arch=(any)
url="https://github.com/FFY00/pulseaudio-equalizer-ladspa"
license=('GPL3')
depends=('pygtk' 'swh-plugins' 'gnome-icon-theme' 'pulseaudio' 'bc')
makedepends=('git')
source=(
  "${pkgname%-git}::git+https://github.com/FFY00/pulseaudio-equalizer-ladspa"
)
md5sums=(
  'SKIP'
)

package() {
  echo "$pkgdir"
  cd "$srcdir/pulseaudio-equalizer-ladspa-ffy00"
  cp -rfp equalizerrc "$pkgdir"
  cp -rfp share "$pkgdir"
  cp -rfp bin "$pkgdir"
}
