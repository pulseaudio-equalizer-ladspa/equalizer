#!/usr/bin/python
# -*- coding: utf-8 -*-

# PulseAudio Equalizer (PyGTK Interface)
#
# Intended for use in conjunction with pulseaudio-equalizer script
#
# Author: Conn O'Griofa <connogriofa AT gmail DOT com>
# Version: (see '/usr/pulseaudio-equalizer' script)
#

try:
    from gi import pygtkcompat
except ImportError:
    pygtkcompat = None
    print('Compat not found')

if pygtkcompat is not None:
    pygtkcompat.enable() 
    pygtkcompat.enable_gtk(version='3.0')

#import pygtk
#pygtk.require('2.0')
import gtk
import gobject
import os

configdir = os.getenv('HOME') + '/.config/pulse'
eqconfig = configdir + '/equalizerrc'
eqconfig2 = configdir + '/equalizerrc.test'
eqpresets = eqconfig + '.availablepresets'
presetdir1 = configdir + '/presets'
presetdir2 = '/usr/share/pulseaudio-equalizer/presets'


def GetSettings():
    global rawdata
    global rawpresets
    global ladspa_filename
    global ladspa_name
    global ladspa_label
    global preamp
    global num_ladspa_controls
    global ladspa_controls
    global ladspa_inputs
    global status
    global realstatus
    global persistence
    global preset
    global ranges
    global windowtitle
    global presetmatch
    global clearpreset

    print('Getting settings...')

    os.system('pulseaudio-equalizer interface.getsettings')

    f = open(eqconfig, 'r')
    rawdata = f.read().split('\n')
    f.close()

    rawpresets = {}
    f = open(eqpresets, 'r')
    rawpresets = f.read().split('\n')
    f.close()
    del rawpresets[len(rawpresets) - 1]

    ladspa_filename = str(rawdata[0])
    ladspa_name = str(rawdata[1])
    ladspa_label = str(rawdata[2])
    preamp = rawdata[3]
    preset = str(rawdata[4])
    status = int(rawdata[5])
    persistence = int(rawdata[6])
    ranges = rawdata[7:9]
    num_ladspa_controls = int(rawdata[9])
    ladspa_controls = rawdata[10:10 + num_ladspa_controls]
    ladspa_inputs = rawdata[10 + num_ladspa_controls:10 + num_ladspa_controls + num_ladspa_controls]

    if status == 1:
        realstatus = 'Enabled'
    else:
        realstatus = 'Disabled'

    windowtitle = 'PulseAudio ' + ladspa_label

    clearpreset = 1
    presetmatch = ''
    for i in range(len(rawpresets)):
        if rawpresets[i] == preset:
            print('Match!')
            presetmatch = 1


def ApplySettings():
    print('Applying settings...')
    f = open(eqconfig, 'w')
    del rawdata[:]
    rawdata.append(str(ladspa_filename))
    rawdata.append(str(ladspa_name))
    rawdata.append(str(ladspa_label))
    rawdata.append(str(preamp))
    rawdata.append(str(preset))
    rawdata.append(str(status))
    rawdata.append(str(persistence))
    for i in range(2):
        rawdata.append(str(ranges[i]))
    rawdata.append(str(num_ladspa_controls))
    for i in range(num_ladspa_controls):
        rawdata.append(str(ladspa_controls[i]))
    for i in range(num_ladspa_controls):
        rawdata.append(str(ladspa_inputs[i]))

    for i in rawdata:
        f.write(str(i) + '\n')
    f.close()

    os.system('pulseaudio-equalizer interface.applysettings')


def FormatLabels(x):
    global c
    global suffix
    global whitespace1
    global whitespace2

    whitespace1 = ''
    whitespace2 = ''

    current_input = int(ladspa_inputs[x - 1])
    if current_input < 99:
        a = current_input
        suffix = 'Hz'
    if current_input > 99 and current_input < 999:
        a = current_input
        suffix = 'Hz'
    if current_input > 999 and current_input < 9999:
        a = float(current_input) / 1000
        suffix = 'KHz'
    if current_input > 9999:
        a = float(current_input) / 1000
        suffix = 'KHz'

    # Filter out unnecessary ".0" from ladspa_inputs
    b = str(a)
    if b[-2:] == '.0':
        c = b[:-2]
    else:
        c = b

    # Add whitespace formatting to ensure text is centered
    if len(c) == 3 and len(suffix) == 2:
        whitespace2 = ' '
    if len(c) < 4 and len(suffix) == 3:
        whitespace1 = ' '
    if len(c) < 2 and len(suffix) == 3:
        whitespace1 = '  '


class Equalizer:

    def on_scale(self, widget, y):
        global ladspa_controls
        global preset
        global clearpreset
        newvalue = float(round(widget.get_value(), 1))
        del ladspa_controls[y - 1]
        ladspa_controls.insert(y - 1, newvalue)
        if clearpreset == 1:
            preset = ''
            presetsbox.get_child().set_text(preset)
        for i in range(1, num_ladspa_controls + 1):
            self.scalevalues[i].set_markup('<small>' + str(float(ladspa_controls[i - 1])) + '\ndB</small>')

    def on_presetsbox(self, widget, x):
        global preset
        global presetmatch
        global clearpreset
        global ladspa_filename
        global ladspa_name
        global ladspa_label
        global preamp
        global num_ladspa_controls
        global ladspa_controls
        global ladspa_inputs
        global windowtitle
        preset = presetsbox.get_child().get_text()

        presetmatch = ''
        for i in range(len(rawpresets)):
            if rawpresets[i] == preset:
                print('Match!')
                presetmatch = 1

        if presetmatch == 1:
            if os.path.isfile(presetdir1 + '/' + preset + '.preset'):
                f = open(presetdir1 + '/' + preset + '.preset', 'r')
                rawdata = f.read().split('\n')
                f.close
            elif os.path.isfile(presetdir2 + '/' + preset + '.preset'):
                f = open(presetdir2 + '/' + preset + '.preset', 'r')
                rawdata = f.read().split('\n')
                f.close
            else:
                print("Can't find %s preset" % preset)

            ladspa_filename = str(rawdata[0])
            ladspa_name = str(rawdata[1])
            ladspa_label = str(rawdata[2])
            #preamp = (rawdata[3])
            preset = str(rawdata[4])
            num_ladspa_controls = int(rawdata[5])
            ladspa_controls = rawdata[6:6 + num_ladspa_controls]
            ladspa_inputs = rawdata[6 + num_ladspa_controls:6 + num_ladspa_controls + num_ladspa_controls]

            preampscale.set_value(float(preamp))
            preampscalevalue.set_markup(str(preampscale.get_value())
                    + 'x')
            windowtitle = 'PulseAudio ' + ladspa_label
            self.window.set_title(windowtitle + ' [' + realstatus + ']')
            clearpreset = ''
            for i in range(1, num_ladspa_controls + 1):
                self.scales[i].set_value(float(ladspa_controls[i - 1]))
                FormatLabels(i)
                self.labels[i].set_markup('<small>' + whitespace1 + c + '\n' + whitespace2 + suffix + '</small>')
                self.scalevalues[i].set_markup('<small>' + str(float(ladspa_controls[i - 1])) + '\ndB</small>')

            # Set preset again due to interference from scale modifications
            preset = str(rawdata[4])
            clearpreset = 1
            presetsbox.get_child().set_text(preset)
            ApplySettings()

    def on_applysettings(self, widget):
        ApplySettings()

    def on_resetsettings(self, widget):
        print('Resetting to defaults...')
        os.system('pulseaudio-equalizer interface.resetsettings')
        GetSettings()

        eqenabled.set_active(status)
        keepsettings.set_active(persistence)
        presetsbox.get_child().set_text(preset)
        preampscale.set_value(float(preamp))
        for i in range(1, num_ladspa_controls + 1):
            self.scales[i].set_value(float(ladspa_controls[i - 1]))
            FormatLabels(i)
            self.labels[i].set_markup('<small>' + whitespace1 + c + '\n' + whitespace2 + suffix + '</small>')
            self.scalevalues[i].set_markup('<small>' + str(float(ladspa_controls[i - 1])) + '\ndB</small>')

    def on_savepreset(self, widget):
        global preset
        global presetmatch
        preset = presetsbox.get_child().get_text()
        if preset == '' or presetmatch == 1:
            print('Invalid preset name')
        else:
            f = open(presetdir1 + '/' + preset + '.preset', 'w')

            del rawdata[:]
            rawdata.append(str(ladspa_filename))
            rawdata.append(str(ladspa_name))
            rawdata.append(str(ladspa_label))
            rawdata.append(str(preamp))
            rawdata.append(str(preset))
            rawdata.append(str(num_ladspa_controls))
            for i in range(num_ladspa_controls):
                rawdata.append(str(ladspa_controls[i]))
            for i in range(num_ladspa_controls):
                rawdata.append(str(ladspa_inputs[i]))

            for i in rawdata:
                f.write(str(i) + '\n')
            f.close()

            # Clear preset list from ComboBox
            for i in range(len(rawpresets)):
                presetsbox.remove_text(0)

            # Apply settings (which will save new preset as default)
            ApplySettings()

            # Refresh (and therefore, sort) preset list
            GetSettings()

            # Repopulate preset list into ComboBox
            for i in range(len(rawpresets)):
                presetsbox.append_text(rawpresets[i])

    def on_preampscale(self, widget):
        global preamp
        preamp = float(round(widget.get_value(), 1))
        preampscalevalue.set_markup(str(preamp) + 'x')
        # preset = ''
        # presetsbox.get_child().set_text(preset)

    def on_eqenabled(self, widget):
        global status
        if widget.get_active():
            self.window.set_title(windowtitle + ' [Enabled]')
            status = 1
        else:
            self.window.set_title(windowtitle + ' [Disabled]')
            status = 0
        ApplySettings()

    def on_keepsettings(self, widget):
        global persistence
        if widget.get_active():
            persistence = 1
        else:
            persistence = 0
        ApplySettings()

    def on_removepreset(self, widget):
        global preset
        global presets
        dialog = gtk.FileChooserDialog('Choose preset to remove...',
                None, gtk.FILE_CHOOSER_ACTION_OPEN, (gtk.STOCK_CANCEL,
                gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)

        filter = gtk.FileFilter()
        filter.set_name('Preset files')
        filter.add_pattern('*.preset')
        dialog.add_filter(filter)
        dialog.set_current_folder(presetdir1)
        dialog.show()

        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            filename = dialog.get_filename()
            path_and_name = os.path.split(filename)
            name = path_and_name[1]
            os.remove(filename)

            # Make a note of the current preset, then clear it temporarily
            preset = presetsbox.get_child().get_text()
            realpreset = preset
            preset = ''
            presetsbox.get_child().set_text('')

            # Clear preset list from ComboBox
            for i in range(len(rawpresets)):
                presetsbox.remove_text(0)

            # Refresh (and therefore, sort) preset list
            GetSettings()

            # Clear preset (if it is the same as removed preset), or restore preset
            if presetdir1 + '/' + preset + '.preset' == filename:
                preset = ''
            else:
                preset = realpreset

            # Restore preset
            presetsbox.get_child().set_text(preset)

            # Repopulate preset list into ComboBox
            for i in range(len(rawpresets)):
                presetsbox.append_text(rawpresets[i])

            # Apply settings
            ApplySettings()

        dialog.destroy()

    def destroy_equalizer(self, widget, data=None):
        gtk.main_quit()

    def __init__(self):
        GetSettings()

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_resizable(True)

        self.window.connect('destroy', self.destroy_equalizer)
        self.window.set_title(windowtitle + ' [' + realstatus + ']')
        self.window.set_border_width(0)

        icon_theme = gtk.icon_theme_get_default()
        icon_theme = gtk.icon_theme_get_default()
        if icon_theme.has_icon('multimedia-volume-control'):
            icon = icon_theme.load_icon('multimedia-volume-control',
                    16, 0)
            self.window.set_icon(icon)
        elif icon_theme.has_icon('gnome-volume-control'):
            icon = icon_theme.load_icon('gnome-volume-control', 16, 0)
            self.window.set_icon(icon)
        elif icon_theme.has_icon('stock_volume'):
            icon = icon_theme.load_icon('stock_volume', 16, 0)
            self.window.set_icon(icon)
        else:
            print('No icon found, window will be iconless')

        menu = gtk.Menu()

        menu_item = gtk.MenuItem('Reset to defaults')
        menu_item.connect('activate', self.on_resetsettings)
        menu.append(menu_item)
        menu_item.show()
        menu_item = gtk.MenuItem('Remove user preset...')
        menu_item.connect('activate', self.on_removepreset)
        menu.append(menu_item)
        menu_item.show()
        root_menu = gtk.MenuItem('Advanced')
        root_menu.show()
        root_menu.set_submenu(menu)

        vbox1 = gtk.VBox(False, 0)
        self.window.add(vbox1)
        vbox1.show()
        menu_bar = gtk.MenuBar()
        vbox1.pack_start(menu_bar, False, False, 2)
        menu_bar.show()
        menu_bar.append(root_menu)

        hbox1 = gtk.HBox(False, 1)
        #hbox1.set_border_width(10)
        vbox1.add(hbox1)
        hbox1.show()

        table = gtk.Table(3, 17, False)
        table.set_border_width(5)
        hbox1.add(table)

        # Preamp widget
        global preampscale
        global preampscalevalue
        preampscale = gtk.VScale()
        preampscale.set_draw_value(0)
        preampscale.set_inverted(1)
        preampscale.set_value_pos(gtk.POS_BOTTOM)
        preampscale.set_range(0.0, 2.0)
        preampscale.set_increments(1, 0.1)
        preampscale.set_digits(1)
        preampscale.set_size_request(35, 200)
        preampscale.set_value(float(preamp))
        preampscale.connect('value-changed', self.on_preampscale)
        label = gtk.Label()
        label.set_markup('<small>Preamp</small>')
        preampscalevalue = gtk.Label()
        preampscalevalue.set_markup(str(preampscale.get_value()) + 'x')
        table.attach(label, 1, 2, 0, 1)
        table.attach(preampscale, 1, 2, 1, 2)
        table.attach(preampscalevalue, 1, 2, 2, 3)
        # label.show()
        # preampscale.show()
        # preampscalevalue.show()

        # Separator between preamp and bands
        separator = gtk.VSeparator()
        table.attach(separator, 2, 3, 1, 2)
        # separator.show()

        # Equalizer bands
        global scale
        self.scales = {}
        self.labels = {}
        self.scalevalues = {}
        for x in range(1, num_ladspa_controls + 1):
            scale = gtk.VScale()
            self.scales[x] = scale
            scale.set_draw_value(0)
            scale.set_inverted(1)
            scale.set_value_pos(gtk.POS_BOTTOM)
            scale.set_range(float(ranges[0]), float(ranges[1]))
            scale.set_increments(1, 0.1)
            scale.set_digits(1)
            scale.set_size_request(35, 200)
            scale.set_value(float(ladspa_controls[x - 1]))
            scale.connect('value-changed', self.on_scale, x)
            FormatLabels(x)
            label = gtk.Label()
            self.labels[x] = label
            label.set_markup('<small>' + whitespace1 + c + '\n'  + whitespace2 + suffix + '</small>')
            scalevalue = gtk.Label()
            self.scalevalues[x] = scalevalue
            scalevalue.set_markup('<small>' + str(scale.get_value())  + '\ndB</small>')
            table.attach(label, x + 2, x + 3, 0, 1)
            table.attach(scale, x + 2, x + 3, 1, 2)
            table.attach(scalevalue, x + 2, x + 3, 2, 3)
            label.show()
            scale.show()
            scalevalue.show()

        table.show()

        vbox2 = gtk.VBox(True, 1)
        vbox2.set_border_width(10)
        hbox1.add(vbox2)
        vbox2.show()

        presetslabel = gtk.Label()
        presetslabel.set_markup('<small>Preset:</small>')
        vbox2.pack_start(presetslabel, False, False, 0)
        presetslabel.show()

        global presetsbox
        presetmodel = gtk.ListStore(str)
        presetsbox = gtk.combo_box_entry_new_with_model(presetmodel)
        presetsbox.set_entry_text_column(0)
        vbox2.pack_start(presetsbox, False, False, 0)
        presetsbox.get_child().set_text(preset)
        for i in range(len(rawpresets)):
            presetsbox.append_text(rawpresets[i])
        presetsbox.connect('changed', self.on_presetsbox, x)
        presetsbox.show()

        savepreset = gtk.Button('Save Preset')
        vbox2.pack_start(savepreset, False, False, 0)
        savepreset.connect('clicked', self.on_savepreset)
        savepreset.show()

        global eqenabled
        eqenabled = gtk.CheckButton('EQ Enabled')
        eqenabled.set_active(status)
        #eqenabled.unset_flags(gtk.CAN_FOCUS)
        eqenabled.connect('clicked', self.on_eqenabled)
        vbox2.pack_start(eqenabled, False, False, 0)
        eqenabled.show()

        global keepsettings
        keepsettings = gtk.CheckButton('Keep Settings')
        keepsettings.set_active(persistence)
        #keepsettings.unset_flags(gtk.CAN_FOCUS)
        keepsettings.connect('clicked', self.on_keepsettings)
        vbox2.pack_start(keepsettings, False, False, 0)
        keepsettings.show()

        applysettings = gtk.Button('Apply Settings')
        vbox2.pack_start(applysettings, False, False, 0)
        applysettings.connect('clicked', self.on_applysettings)
        applysettings.show()

        quitbutton = gtk.Button('Quit')
        vbox2.pack_start(quitbutton, False, False, 0)
        quitbutton.connect('clicked', lambda w: gtk.main_quit())
        quitbutton.show()

        separator = gtk.HSeparator()
        vbox2.pack_start(separator, False, False, 0)
        separator.set_size_request(100, 10)
        # separator.show()

        self.window.show()


def main():
    gtk.main()
    return 0


if __name__ == '__main__':
    Equalizer()
    main()
