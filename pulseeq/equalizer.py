#!/usr/bin/env python
# -*- coding: utf-8 -*-

# PulseAudio Equalizer (PyGTK Interface)
#
# Intended for use in conjunction with pulseaudio-equalizer script
#
# Author: Conn O'Griofa <connogriofa AT gmail DOT com>
# Version: (see '/usr/pulseaudio-equalizer' script)
#

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio

import os, sys

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


@Gtk.Template(resource_path='/com/github/pulseaudio-equalizer-ladspa/Equalizer/ui/Equalizer.ui')
class Equalizer(Gtk.ApplicationWindow):
    __gtype_name__= "Equalizer"

    table = Gtk.Template.Child()
    presetsbox = Gtk.Template.Child()
    eqenabled = Gtk.Template.Child()
    keepsettings = Gtk.Template.Child()

    def on_scale(self, widget, y):
        global ladspa_controls
        global preset
        global clearpreset
        newvalue = float(round(widget.get_value(), 1))
        del ladspa_controls[y - 1]
        ladspa_controls.insert(y - 1, newvalue)
        if clearpreset == 1:
            preset = ''
            self.presetsbox.get_child().set_text(preset)
        for i in range(1, num_ladspa_controls + 1):
            self.scalevalues[i].set_markup('<small>' + str(float(ladspa_controls[i - 1])) + '\ndB</small>')

    @Gtk.Template.Callback()
    def on_presetsbox(self, widget):
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
        preset = self.presetsbox.get_child().get_text()

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
            self.set_title(windowtitle + ' [' + realstatus + ']')
            clearpreset = ''
            for i in range(1, num_ladspa_controls + 1):
                self.scales[i].set_value(float(ladspa_controls[i - 1]))
                FormatLabels(i)
                self.labels[i].set_markup('<small>' + whitespace1 + c + '\n' + whitespace2 + suffix + '</small>')
                self.scalevalues[i].set_markup('<small>' + str(float(ladspa_controls[i - 1])) + '\ndB</small>')

            # Set preset again due to interference from scale modifications
            preset = str(rawdata[4])
            clearpreset = 1
            self.presetsbox.get_child().set_text(preset)
            ApplySettings()

    @Gtk.Template.Callback()
    def on_applysettings(self, widget):
        ApplySettings()

    @Gtk.Template.Callback()
    def on_resetsettings(self, widget):
        print('Resetting to defaults...')
        os.system('pulseaudio-equalizer interface.resetsettings')
        GetSettings()

        self.eqenabled.set_active(status)
        self.keepsettings.set_active(persistence)
        self.presetsbox.get_child().set_text(preset)
        preampscale.set_value(float(preamp))
        for i in range(1, num_ladspa_controls + 1):
            self.scales[i].set_value(float(ladspa_controls[i - 1]))
            FormatLabels(i)
            self.labels[i].set_markup('<small>' + whitespace1 + c + '\n' + whitespace2 + suffix + '</small>')
            self.scalevalues[i].set_markup('<small>' + str(float(ladspa_controls[i - 1])) + '\ndB</small>')

    @Gtk.Template.Callback()
    def on_savepreset(self, widget):
        global preset
        global presetmatch
        preset = self.presetsbox.get_child().get_text()
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
            self.presetsbox.remove_all()

            # Apply settings (which will save new preset as default)
            ApplySettings()

            # Refresh (and therefore, sort) preset list
            GetSettings()

            # Repopulate preset list into ComboBox
            for i in range(len(rawpresets)):
                self.presetsbox.append_text(rawpresets[i])

    def on_preampscale(self, widget):
        global preamp
        preamp = float(round(widget.get_value(), 1))
        preampscalevalue.set_markup(str(preamp) + 'x')
        # preset = ''
        # self.presetsbox.get_child().set_text(preset)

    @Gtk.Template.Callback()
    def on_eqenabled(self, widget):
        global status
        if widget.get_active():
            self.set_title(windowtitle + ' [Enabled]')
            status = 1
        else:
            self.set_title(windowtitle + ' [Disabled]')
            status = 0
        ApplySettings()

    @Gtk.Template.Callback()
    def on_keepsettings(self, widget):
        global persistence
        if widget.get_active():
            persistence = 1
        else:
            persistence = 0
        ApplySettings()

    @Gtk.Template.Callback()
    def on_removepreset(self, widget):
        global preset
        global presets
        dialog = Gtk.FileChooserDialog(title='Choose preset to remove...',
                                       action=Gtk.FileChooserAction.OPEN)
        dialog.add_buttons("_Cancel", Gtk.ResponseType.CANCEL,
                           "_OK", Gtk.ResponseType.OK)
        dialog.set_default_response(Gtk.ResponseType.OK)

        filter = Gtk.FileFilter()
        filter.set_name('Preset files')
        filter.add_pattern('*.preset')
        dialog.add_filter(filter)
        dialog.set_current_folder(presetdir1)
        dialog.show()

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
            path_and_name = os.path.split(filename)
            name = path_and_name[1]
            os.remove(filename)

            # Make a note of the current preset, then clear it temporarily
            preset = self.presetsbox.get_child().get_text()
            realpreset = preset
            preset = ''
            self.presetsbox.get_child().set_text('')

            # Clear preset list from ComboBox
            self.presetsbox.remove_all()

            # Refresh (and therefore, sort) preset list
            GetSettings()

            # Clear preset (if it is the same as removed preset), or restore preset
            if presetdir1 + '/' + preset + '.preset' == filename:
                preset = ''
            else:
                preset = realpreset

            # Restore preset
            self.presetsbox.get_child().set_text(preset)

            # Repopulate preset list into ComboBox
            for i in range(len(rawpresets)):
                self.presetsbox.append_text(rawpresets[i])

            # Apply settings
            ApplySettings()

        dialog.destroy()

    @Gtk.Template.Callback()
    def on_quit(self, widget):
        Gio.Application.get_default().quit()

    def __init__(self, *args, **kwargs):
        super(Equalizer, self).__init__(*args, **kwargs)
        GetSettings()

        self.set_title(windowtitle + ' [' + realstatus + ']')

        # Preamp widget
        global preampscale
        global preampscalevalue
        preampscale = Gtk.Scale(orientation=Gtk.Orientation.VERTICAL)
        preampscale.set_draw_value(0)
        preampscale.set_inverted(1)
        preampscale.set_value_pos(Gtk.PositionType.BOTTOM)
        preampscale.set_range(0.0, 2.0)
        preampscale.set_increments(1, 0.1)
        preampscale.set_digits(1)
        preampscale.set_size_request(35, 200)
        preampscale.set_value(float(preamp))
        preampscale.connect('value-changed', self.on_preampscale)
        label = Gtk.Label()
        label.set_markup('<small>Preamp</small>')
        preampscalevalue = Gtk.Label()
        preampscalevalue.set_markup(str(preampscale.get_value()) + 'x')
        self.table.attach(label, 1, 2, 0, 1)
        self.table.attach(preampscale, 1, 2, 1, 2)
        self.table.attach(preampscalevalue, 1, 2, 2, 3)
        # label.show()
        # preampscale.show()
        # preampscalevalue.show()

        # Separator between preamp and bands
        separator = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        self.table.attach(separator, 2, 3, 1, 2)
        # separator.show()

        # Equalizer bands
        global scale
        self.scales = {}
        self.labels = {}
        self.scalevalues = {}
        for x in range(1, num_ladspa_controls + 1):
            scale = Gtk.Scale(orientation=Gtk.Orientation.VERTICAL)
            self.scales[x] = scale
            scale.set_draw_value(0)
            scale.set_inverted(1)
            scale.set_value_pos(Gtk.PositionType.BOTTOM)
            scale.set_range(float(ranges[0]), float(ranges[1]))
            scale.set_increments(1, 0.1)
            scale.set_digits(1)
            scale.set_size_request(35, 200)
            scale.set_value(float(ladspa_controls[x - 1]))
            scale.connect('value-changed', self.on_scale, x)
            FormatLabels(x)
            label = Gtk.Label()
            self.labels[x] = label
            label.set_markup('<small>' + whitespace1 + c + '\n'  + whitespace2 + suffix + '</small>')
            scalevalue = Gtk.Label()
            self.scalevalues[x] = scalevalue
            scalevalue.set_markup('<small>' + str(scale.get_value())  + '\ndB</small>')
            self.table.attach(label, x + 2, x + 3, 0, 1)
            self.table.attach(scale, x + 2, x + 3, 1, 2)
            self.table.attach(scalevalue, x + 2, x + 3, 2, 3)
            label.show()
            scale.show()
            scalevalue.show()

        self.presetsbox.get_child().set_text(preset)
        for i in range(len(rawpresets)):
            self.presetsbox.append_text(rawpresets[i])

        self.eqenabled.set_active(status)

        self.keepsettings.set_active(persistence)

        self.show()


class Application(Gtk.Application):

    def __init__(self, *args, **kwargs):
        super(Application, self).__init__(*args,
            application_id='com.github.pulseaudio-equalizer-ladspa.Equalizer',
            **kwargs)
        self.window = None

    def do_activate(self):
        if not self.window:
            self.window = Equalizer(application=self)

        self.window.present()
