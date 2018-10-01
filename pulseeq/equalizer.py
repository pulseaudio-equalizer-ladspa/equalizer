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
from gi.repository import Gtk, Gio, GLib

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
    global persistence
    global preset
    global ranges
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

        if self.apply_event_source is not None:
            GLib.source_remove (self.apply_event_source);

        self.apply_event_source = GLib.timeout_add (500, self.on_apply_event)

    def on_apply_event(self):
        ApplySettings()
        self.apply_event_source = None
        return False

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
        preset = self.presetsbox.get_child().get_text()

        self.lookup_action('remove').set_enabled(False)

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
                self.lookup_action('remove').set_enabled(True)
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

            self.lookup_action('save').set_enabled(False)
        else:
            self.lookup_action('save').set_enabled(preset != '')

    def on_resetsettings(self, action=None, param=None):
        print('Resetting to defaults...')
        os.system('pulseaudio-equalizer interface.resetsettings')
        GetSettings()

        self.lookup_action('eqenabled').set_state(GLib.Variant('b', status))
        Gio.Application.get_default().lookup_action('keepsettings').set_state(GLib.Variant('b', persistence))
        self.presetsbox.get_child().set_text(preset)
        preampscale.set_value(float(preamp))
        for i in range(1, num_ladspa_controls + 1):
            self.scales[i].set_value(float(ladspa_controls[i - 1]))
            FormatLabels(i)
            self.labels[i].set_markup('<small>' + whitespace1 + c + '\n' + whitespace2 + suffix + '</small>')
            self.scalevalues[i].set_markup('<small>' + str(float(ladspa_controls[i - 1])) + '\ndB</small>')

    def on_savepreset(self, action, param):
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

            action.set_enabled(False)
            self.lookup_action('remove').set_enabled(True)

    def on_preampscale(self, widget):
        global preamp
        preamp = float(round(widget.get_value(), 1))
        preampscalevalue.set_markup(str(preamp) + 'x')
        # preset = ''
        # self.presetsbox.get_child().set_text(preset)

    def on_eqenabled(self, action, state):
        global status
        status = int(state.get_boolean())
        ApplySettings()
        action.set_state(state)

    def on_removepreset(self, action, param):
        global preset
        os.remove(presetdir1 + '/' + preset + '.preset')

        self.presetsbox.get_child().set_text('')

        # Clear preset list from ComboBox
        self.presetsbox.remove_all()

        # Refresh (and therefore, sort) preset list
        GetSettings()

        # Repopulate preset list into ComboBox
        for i in range(len(rawpresets)):
            self.presetsbox.append_text(rawpresets[i])

        preset = ''
        # Apply settings
        ApplySettings()

        action.set_enabled(False)

    @Gtk.Template.Callback()
    def on_quit(self, object=None, param=None):
        Gio.Application.get_default().quit()

    def __init__(self, *args, **kwargs):
        super(Equalizer, self).__init__(*args, **kwargs)
        GetSettings()

        self.apply_event_source = None

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

        action = Gio.SimpleAction.new('save', None)
        action.set_enabled(False)
        action.connect('activate', self.on_savepreset)
        self.add_action(action)

        action = Gio.SimpleAction.new('remove', None)
        action.set_enabled(False)
        action.connect('activate', self.on_removepreset)
        self.add_action(action)

        self.presetsbox.get_child().set_text(preset)
        for i in range(len(rawpresets)):
            self.presetsbox.append_text(rawpresets[i])

        action = Gio.SimpleAction.new_stateful('eqenabled', None,
                                               GLib.Variant('b', status))
        action.connect('change-state', self.on_eqenabled)
        self.add_action(action)

        self.show()


class Application(Gtk.Application):

    def __init__(self, *args, **kwargs):
        super(Application, self).__init__(*args,
            application_id='com.github.pulseaudio-equalizer-ladspa.Equalizer',
            resource_base_path='/com/github/pulseaudio-equalizer-ladspa/Equalizer',
            **kwargs)

        self.window = None

    def do_startup(self):
        Gtk.Application.do_startup(self)
        GetSettings()

        self.window = Equalizer(application=self)

        action = Gio.SimpleAction.new('resetsettings', None)
        action.connect('activate', self.window.on_resetsettings)
        self.add_action(action)

        global persistence
        action = Gio.SimpleAction.new_stateful('keepsettings', None,
                                               GLib.Variant('b', persistence))
        action.connect('change-state', self.on_keepsettings)
        self.add_action(action)

        action = Gio.SimpleAction.new('quit', None)
        action.connect('activate', self.window.on_quit)
        self.add_action(action)

    def do_activate(self):
        if not self.window:
            self.window = Equalizer(application=self)

        self.window.present()

    def on_keepsettings(self, action, state):
        global persistence
        persistence = int(state.get_boolean())
        ApplySettings()
        action.set_state(state)
