#!/usr/bin/python3
# -*- coding: utf-8 -*-

# PulseAudio Equalizer (PyGtk Interface)
# version: 2021.11
#
# Maintainer: Luis Armando Medina Avitia <lamedina AT gmail DOT com>
#
# Intended for use in conjunction with pulseaudio-equalizer script
#
# Author: Conn O'Griofa <connogriofa AT gmail DOT com>
# Version: (see '/usr/pulseaudio-equalizer' script)
#

import gi
gi.check_version('3.30')
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio, GLib
import os, sys

if 'PULSE_CONFIG_PATH' in os.environ:
    CONFIG_DIR = os.getenv('PULSE_CONFIG_PATH')
elif 'XDG_CONFIG_HOME' in os.environ:
    CONFIG_DIR = os.path.join(os.getenv('XDG_CONFIG_HOME'), 'pulse')
else:
    CONFIG_DIR = os.path.join(os.getenv('HOME'), '.config', 'pulse')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'equalizerrc')
PRESETS_FILE = os.path.join(CONFIG_DIR, 'equalizerrc.availablepresets')
USER_PRESET_DIR = os.path.join(CONFIG_DIR, 'presets')
SYSTEM_PRESET_DIR = os.path.join('@pkgdatadir@', 'presets')
if os.environ.get('GNOME_DESKTOP_SESSION_ID'):
    DESKTOP_ENVIRONMENT = "Gnome"
else:
    DESKTOP_ENVIRONMENT = os.environ.get('DESKTOP_SESSION')


#import Gtk
#import gobject
from urllib.request import url2pathname, urlparse, unquote
from gi.repository import GdkPixbuf, Gdk

configdir = os.getenv('HOME') + '/.config/pulse'
eqconfig = configdir + '/equalizerrc'
eqconfig2 = configdir + '/equalizerrc.test'
eqpresets = eqconfig + '.availablepresets'
presetdir1 = configdir + '/presets'
presetdir2 = '/usr/share/pulseaudio-equalizer/presets'

TARGET_TYPE_URI_LIST = 80

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
    global boxindex
    global headerbar
    global change_scale

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

    rawpresets = list(set(rawpresets))
    rawpresets.sort()

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
    #headerbar = int(rawdata[11])

    if status == 1:
        realstatus = 'Enabled'
    else:
        realstatus = 'Disabled'

    windowtitle = 'PulseAudio ' + ladspa_label

    clearpreset = 1
    presetmatch = ''
    boxindex    = -1

    for i in range(len(rawpresets)):
        if rawpresets[i] == preset:
            print('Match!')
            presetmatch = 1
            boxindex = i


def ApplySettings():
    global change_scale
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
    #rawdata.append(str(headerbar))
    f.close()

    os.system('pulseaudio-equalizer interface.applysettings')
    change_scale = 0

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

@Gtk.Template(filename='../share/pulseaudio-equalizer/equalizer.ui')
class Equalizer(Gtk.ApplicationWindow):
    __gtype_name__= "Equalizer"

    grid = Gtk.Template.Child()
    headerbarcheck: Gtk.CheckMenuItem = Gtk.Template.Child()
    savehdr: Gtk.Button = Gtk.Template.Child()
    deletehdr: Gtk.Button = Gtk.Template.Child()
    menuhdr: Gtk.MenuButton = Gtk.Template.Child()
    presetsbox = Gtk.Template.Child()
    activehdr: Gtk.Switch = Gtk.Template.Child()
    presetsbox1 = Gtk.Template.Child()
    about_headerbar: Gtk.ImageMenuItem = Gtk.Template.Child()

    new_preset: Gtk.Entry = Gtk.Template.Child('new_preset')

    menustd: Gtk.MenuBar = Gtk.Template.Child()
    actionbar: Gtk.ActionBar = Gtk.Template.Child()

    window_about = Gtk.Template.Child('About')
    window_title: Gtk.Label = Gtk.Template.Child('title')
    window_save = Gtk.Template.Child('Save_dialog')

    def on_scale(self, widget, y):
        global ladspa_controls
        global preset
        global clearpreset
        global change_scale

        print("on_scale")
        newvalue = float(round(widget.get_value(), 1))
        ladspa_controls[y] = newvalue
        
        change_scale = 1

        if clearpreset == 1:
            preset = ''
            presetmatch = ''
            self.presetsbox.get_child().set_text(preset)
            self.presetsbox1.get_child().set_text(preset)

        self.scalevalues[y].set_markup('<small>' + str(float(ladspa_controls[y])) + '\ndB</small>')

        if self.apply_event_source is not None:
            GLib.source_remove (self.apply_event_source);

        self.apply_event_source = GLib.timeout_add (500, self.on_apply_event)

    def on_apply_event(self):
        global change_scale
        global presetmatch
        print("on_apply_event")
        print(f"change_scale: {change_scale}")
        print(f"presetmatch: {presetmatch}")
        ApplySettings()
        self.apply_event_source = None
        if change_scale == 1 and  presetmatch == 1 :
            presetmatch = ''
        change_scale = 0
        print(f"change_scale: {change_scale}")
        print(f"presetmatch: {presetmatch}")

        return False


    @Gtk.Template.Callback()
    def on_headerbarcheck(self, widget, **_kwargs):
        global preset
        print("on_headerbarcheck")
        assert self.headerbarcheck == widget
        #print(dir(widget))
        if self.headerbarcheck.get_active() :
            #print('activo')
            self.savehdr.set_visible(True)
            self.deletehdr.set_visible(True)
            self.menuhdr.set_visible(True)
            self.presetsbox.set_visible(True)
            self.activehdr.set_visible(True)
            self.menustd.set_visible(False)
            self.actionbar.set_visible(False)
            self.about_headerbar.set_visible(True)
            self.window_title.set_visible(False)
            self.presetsbox.get_child().set_text(preset)
        else:
            #print('inactivo')
            self.savehdr.set_visible(False)
            self.deletehdr.set_visible(False)
            self.menuhdr.set_visible(False)
            self.presetsbox.set_visible(False)
            self.activehdr.set_visible(False)
            self.menustd.set_visible(True)
            self.actionbar.set_visible(True)
            self.about_headerbar.set_visible(False)
            self.window_title.set_visible(True)
            self.presetsbox1.get_child().set_text(preset)
            

    def update_preset(self):
        global preset
        global presetmatch
        global clearpreset
        global ladspa_filename
        global ladspa_name
        global ladspa_label
        global num_ladspa_controls
        global ladspa_controls
        global ladspa_inputs

        print("update_preset")

        self.lookup_action('remove').set_enabled(False)
        print("before check:",presetmatch)
        presetmatch = ''
        for i in range(len(rawpresets)):
            if rawpresets[i] == preset:
                print('Match!')
                presetmatch = 1

        print('presetsbox',self.presetsbox.get_child().get_text())
        print('presetsbox1',self.presetsbox1.get_child().get_text())
        print("after check:",presetmatch)


        if presetmatch == 1:
            if os.path.isfile(os.path.join(USER_PRESET_DIR, preset + '.preset')):
                f = open(os.path.join(USER_PRESET_DIR, preset + '.preset'), 'r')
                rawdata = f.read().split('\n')
                f.close
                self.lookup_action('remove').set_enabled(True)
            elif os.path.isfile(os.path.join(SYSTEM_PRESET_DIR, preset + '.preset')):
                f = open(os.path.join(SYSTEM_PRESET_DIR, preset + '.preset'), 'r')
                rawdata = f.read().split('\n')
                f.close
            else:
                print("Can't find %s preset" % preset)

            ladspa_filename = str(rawdata[0])
            ladspa_name = str(rawdata[1])
            ladspa_label = str(rawdata[2])
            preset = str(rawdata[4])
            num_ladspa_controls = int(rawdata[5])
            ladspa_controls = rawdata[6:6 + num_ladspa_controls]
            ladspa_inputs = rawdata[6 + num_ladspa_controls:6 + num_ladspa_controls + num_ladspa_controls]

            clearpreset = ''
            for i in range(num_ladspa_controls):
                self.scales[i].set_value(float(ladspa_controls[i]))
                self.labels[i].set_frequency(ladspa_inputs[i])
                self.scalevalues[i].set_markup('<small>' + str(float(ladspa_controls[i])) + '\ndB</small>')

            # Set preset again due to interference from scale modifications
            preset = str(rawdata[4])
            clearpreset = 1
            if self.headerbarcheck.get_active() :
                self.presetsbox.get_child().set_text(preset)
            else:
                self.presetsbox1.get_child().set_text(preset)
            ApplySettings()

            #self.lookup_action('save').set_enabled(False)
        else:
            pass
            #self.lookup_action('save').set_enabled(preset != '')


    @Gtk.Template.Callback()
    def on_presetsbox(self, widget):
        global preset
        global clearpreset
        global presetmatch
        global change_scale

        print("on_presetsbox")
        presetmatch = ''

        print(f"preset: {preset}")
        print(f"clearpreset: {clearpreset}")
        print(f"presetmatch: {presetmatch}")
        
        active_hdr = self.headerbarcheck.get_active()
        print(f"header: {active_hdr}")

        if self.headerbarcheck.get_active() :
            if not change_scale :
                if len(self.presetsbox.get_child().get_text()) > 0 :
                    preset = self.presetsbox.get_child().get_text()
                    #self.presetsbox1.get_child().set_text(preset)
                    self.update_preset()
                change_scale = 0    
        else:
            if not change_scale :
                if len(self.presetsbox1.get_child().get_text()) > 0 :
                    preset = self.presetsbox1.get_child().get_text()
                   #self.presetsbox.get_child().set_text(preset)
                    self.update_preset()
                change_scale = 0

    def on_resetsettings(self, action=None, param=None):
        print('Resetting to defaults...')
        os.system('pulseaudio-equalizer interface.resetsettings')
        GetSettings()

        self.lookup_action('eqenabled').set_state(GLib.Variant('b', status))
        Gio.Application.get_default().lookup_action('keepsettings').set_state(GLib.Variant('b', persistence))
        self.presetsbox.get_child().set_text(preset)
        self.presetsbox1.get_child().set_text(preset)
        for i in range(num_ladspa_controls):
            self.scales[i].set_value(float(ladspa_controls[i]))
            self.labels[i].set_frequency(ladspa_inputs[i])
            self.scalevalues[i].set_markup('<small>' + str(float(ladspa_controls[i])) + '\ndB</small>')

    def on_savepreset(self, action, param):
        global preset
        global presetmatch
        global presetmatch1

        print("on_savepreset")

        preset = self.presetsbox.get_child().get_text()
        if preset == '' or presetmatch == 1:
            print('Invalid preset name')
        else:
            f = open(os.path.join(USER_PRESET_DIR, preset + '.preset'), 'w')

            del rawdata[:]
            rawdata.append(str(ladspa_filename))
            rawdata.append(str(ladspa_name))
            rawdata.append(str(ladspa_label))
            rawdata.append('')
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
            self.presetsbox1.remove_all()


            # Apply settings (which will save new preset as default)
            ApplySettings()

            # Refresh (and therefore, sort) preset list
            GetSettings()

            # Repopulate preset list into ComboBox
            for i in range(len(rawpresets)):
                self.presetsbox.append_text(rawpresets[i])
                self.presetsbox1.append_text(rawpresets[i])

            action.set_enabled(False)
            self.lookup_action('remove').set_enabled(True)

    def on_eqenabled(self, action, state):
        global status
        status = int(state.get_boolean())
        ApplySettings()
        action.set_state(state)

    def on_removepreset(self, action, param):
        global preset
        os.remove(os.path.join(USER_PRESET_DIR, preset + '.preset'))

        self.presetsbox.get_child().set_text('')
        self.presetsbox1.get_child().set_text('')

        # Clear preset list from ComboBox
        self.presetsbox.remove_all()
        self.presetsbox1.remove_all()

        # Refresh (and therefore, sort) preset list
        GetSettings()

        # Repopulate preset list into ComboBox
        for i in range(len(rawpresets)):
            self.presetsbox.append_text(rawpresets[i])
            self.presetsbox1.append_text(rawpresets[i])

        preset = ''
        # Apply settings
        ApplySettings()

        action.set_enabled(False)

    @Gtk.Template.Callback()
    def on_delete(self, widget):
        global preset
        os.remove(os.path.join(USER_PRESET_DIR, preset + '.preset'))

        self.presetsbox.get_child().set_text('')
        self.presetsbox1.get_child().set_text('')

        # Clear preset list from ComboBox
        self.presetsbox.remove_all()
        self.presetsbox1.remove_all()

        # Refresh (and therefore, sort) preset list
        GetSettings()

        # Repopulate preset list into ComboBox
        for i in range(len(rawpresets)):
            self.presetsbox.append_text(rawpresets[i])
            self.presetsbox1.append_text(rawpresets[i])

        preset = ''
        # Apply settings
        ApplySettings()

        action.set_enabled(False)

    @Gtk.Template.Callback()
    def on_about_activate(self, widget):
        result = self.window_about.run()
        if result == -4 :
            self.window_about.hide()

    @Gtk.Template.Callback()
    def on_about_close(self, widget):
        self.window_about.hide()

    @Gtk.Template.Callback()
    def on_save(self, widget):
        global preset
        global presetmatch
        global presetmatch1

        self.new_preset.set_text('')
        result = self.window_save.run()
        print(result)
        if result == -6 or result == -4 :
            self.window_save.hide()
        elif result == Gtk.ResponseType.ACCEPT :
            #save new preset

            preset = self.new_preset.get_text()

            print(preset)
            print(presetmatch)

            if preset == '' or presetmatch == 1:
                print('Invalid preset name')
            else:
                f = open(os.path.join(USER_PRESET_DIR, preset + '.preset'), 'w')

                del rawdata[:]
                rawdata.append(str(ladspa_filename))
                rawdata.append(str(ladspa_name))
                rawdata.append(str(ladspa_label))
                rawdata.append('')
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
                self.presetsbox1.remove_all()

                # Apply settings (which will save new preset as default)
                ApplySettings()

                # Refresh (and therefore, sort) preset list
                GetSettings()

                # Repopulate preset list into ComboBox
                for i in range(len(rawpresets)):
                    self.presetsbox.append_text(rawpresets[i])
                    self.presetsbox1.append_text(rawpresets[i])

                #action.set_enabled(False)
                self.lookup_action('remove').set_enabled(True)

                if self.headerbarcheck.get_active() :
                    self.presetsbox.get_child().set_text(preset)
                else:
                    self.presetsbox1.get_child().set_text(preset)
                presetmatch = 1

            self.window_save.hide()

    @Gtk.Template.Callback()
    def on_save_close(self, widget):
        self.window_save.hide()

    def __init__(self, *args, **kwargs):
        super(Equalizer, self).__init__(*args, **kwargs)
        global headerbar
        global change_scale
        GetSettings()

        self.apply_event_source = None

        headerbar = 0
        change_scale = 0
        if headerbar :
            #print('activo')
            self.savehdr.set_visible(True)
            self.deletehdr.set_visible(True)
            self.menuhdr.set_visible(True)
            self.presetsbox.set_visible(True)
            self.activehdr.set_visible(True)
            self.menustd.set_visible(False)
            self.actionbar.set_visible(False)
            self.about_headerbar.set_visible(True)
            self.window_title.set_visible(False)
        else:
            #print('inactivo')
            self.savehdr.set_visible(False)
            self.deletehdr.set_visible(False)
            self.menuhdr.set_visible(False)
            self.presetsbox.set_visible(False)
            self.activehdr.set_visible(False)
            self.menustd.set_visible(True)
            self.actionbar.set_visible(True)
            self.about_headerbar.set_visible(False)
            self.window_title.set_visible(True)

        # Equalizer bands
        global scale
        self.scales = {}
        self.labels = {}
        self.scalevalues = {}
        for x in range(num_ladspa_controls):
            scale = Gtk.Scale(orientation=Gtk.Orientation.VERTICAL,
                              draw_value=False, inverted=True, digits=1,
                              expand=True, visible=True)
            self.scales[x] = scale
            scale.set_range(float(ranges[0]), float(ranges[1]))
            scale.set_increments(1, 0.1)
            scale.set_size_request(35, 200)
            scale.set_value(float(ladspa_controls[x]))
            scale.connect('value-changed', self.on_scale, x)
            label = FrequencyLabel(frequency = ladspa_inputs[x])
            self.labels[x] = label
            scalevalue = Gtk.Label(visible=True, use_markup=True,
                label='<small>' + str(scale.get_value())  + '\ndB</small>')
            self.scalevalues[x] = scalevalue
            self.grid.attach(label, x, 0, 1, 1)
            self.grid.attach(scale, x, 1, 1, 2)
            self.grid.attach(scalevalue, x, 3, 1, 1)

        action = Gio.SimpleAction.new('save', None)
        #action.set_enabled(False)
        action.connect('activate', self.on_savepreset)
        self.add_action(action)

        action = Gio.SimpleAction.new('on_save', None)
        action.connect('activate', self.on_save)
        self.add_action(action)

        action = Gio.SimpleAction.new('save_close', None)
        action.connect('activate', self.on_save_close)
        self.add_action(action)

        action = Gio.SimpleAction.new('remove', None)
        action.set_enabled(False)
        action.connect('activate', self.on_removepreset)
        self.add_action(action)

        action = Gio.SimpleAction.new('on_delete', None)
        action.connect('activate', self.on_delete)
        self.add_action(action)
   

        self.presetsbox.get_child().set_text(preset)
        self.presetsbox1.get_child().set_text(preset)
        for i in range(len(rawpresets)):
            self.presetsbox.append_text(rawpresets[i])
            self.presetsbox1.append_text(rawpresets[i])

        action = Gio.SimpleAction.new_stateful('eqenabled', None,
                                               GLib.Variant('b', status))
        action.connect('change-state', self.on_eqenabled)
        self.add_action(action)

        action = Gio.SimpleAction.new('about', None)
        action.connect('activate', self.on_about_activate)
        self.add_action(action)

        action = Gio.SimpleAction.new('about_close', None)
        action.connect('activate', self.on_about_close)
        self.add_action(action)

        self.show()
        

class FrequencyLabel(Gtk.Label):
    def __init__(self, frequency=None):
        super(FrequencyLabel, self).__init__(visible=True, use_markup=True,
                                             justify=Gtk.Justification.CENTER)
        if frequency is not None:
            self.set_frequency(frequency)

    def set_frequency(self, frequency):
        frequency = float(frequency)
        suffix = 'Hz'

        if frequency > 999:
            frequency = frequency / 1000
            suffix = 'KHz'

        self.set_label('<small>{0:g}\n{1}</small>'.format(frequency, suffix))


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
        action.connect('activate', self.on_quit)
        self.add_action(action)

        action = Gio.SimpleAction.new('headerbarcheck', None)
        action.connect('activate', self.window.on_headerbarcheck)
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

    def on_quit(self, action, param):
        Gio.Application.get_default().quit()




app = Application()
app.run(sys.argv)