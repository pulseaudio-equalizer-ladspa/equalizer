#!/usr/bin/python3
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
from gi.repository import GdkPixbuf

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
    global boxindex

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
    boxindex    = -1

    for i in range(len(rawpresets)):
        if rawpresets[i] == preset:
            print('Match!')
            presetmatch = 1
            boxindex = i


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

class AboutDialog(gtk.AboutDialog):
    def __init__(self):

        logoPath = '/usr/share/pulseaudio-equalizer/pulseaudio-equalizer-logo.png'

        gtk.AboutDialog.__init__(self)
        self.set_title("AboutDialog")
        self.set_program_name("Pulseaudio Equalizer")
        self.set_version("2.7.2")
        self.set_comments("A LADSPA based multiband equalizer for getting better sound out of pulseaudio")
        self.set_website("https://github.com/larmedina75/pulseaudio-equalizer-ladspa")
        self.set_website_label("github.com")
        self.set_authors(["Luis Armando Medina https://github.com/larmedina75","Filipe Laíns https://github.com/FFY00", "Conn O Griofa https://launchpad.net/~psyke83", "JuanJo Ciarlante https://github.com/jjo"])
        
        self.connect("response", self.on_response)
        logo = ''
        icon_theme = gtk.icon_theme_get_default()
        if os.path.isfile(logoPath):
            logo = GdkPixbuf.Pixbuf.new_from_file_at_size(logoPath, 64, 64)
        elif icon_theme.has_icon('multimedia-volume-control'):
            logo = icon_theme.load_icon('multimedia-volume-control', 64, 0)
        elif icon_theme.has_icon('gnome-volume-control'):
            logo = icon_theme.load_icon('gnome-volume-control', 64, 0)
        elif icon_theme.has_icon('stock_volume'):
            logo = icon_theme.load_icon('stock_volume', 64, 0)
        else:
            print('No icon found, window will be iconless')
        self.set_logo(logo)

    def on_response(self, dialog, response):
        self.destroy()

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
            #presetsbox.get_child().set_text(preset)
            presetsbox1.set_active(-1)
            savebutton.set_sensitive(True)

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
        global entrypreset
        global savebutton

        #preset = presetsbox.get_child().get_text()
        preset = ""
        tree_iter = presetsbox1.get_active_iter()

        if tree_iter is not None:
            model = presetsbox1.get_model()
            preset = model[tree_iter][0]
            print(model.__dict__)
            print(model[tree_iter][0])

        presetmatch = ''
        boxindex = -1
        for i in range(len(rawpresets)):
            if rawpresets[i] == preset:
                print('Match!', preset )
                presetmatch = 1
                boxindex = i

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
            #presetsbox.get_child().set_text(preset)
            ApplySettings()

            #Disable Save Preset Button (Current config already saved)
            savebutton.set_sensitive(False)

    def on_applysettings(self, widget):
        ApplySettings()

    def on_resetsettings(self, widget):
        print('Resetting to defaults...')
        os.system('pulseaudio-equalizer interface.resetsettings')
        GetSettings()

        eqenabled.set_active(status)
        keepsettings.set_active(persistence)
        #presetsbox.get_child().set_text(preset)
        presetsbox1.set_active(-1)
        preampscale.set_value(float(preamp))
        for i in range(1, num_ladspa_controls + 1):
            self.scales[i].set_value(float(ladspa_controls[i - 1]))
            FormatLabels(i)
            self.labels[i].set_markup('<small>' + whitespace1 + c + '\n' + whitespace2 + suffix + '</small>')
            self.scalevalues[i].set_markup('<small>' + str(float(ladspa_controls[i - 1])) + '\ndB</small>')

    def on_savebutton(self, widget):
        global entrypreset
        global presetsbox1
        global savebutton
        global savepreset

        if not self.savestatus:
            entrypreset.show()
            savepreset.show()
            presetsbox1.hide()

            savebutton.set_label("Cancel")
            self.savestatus = 1
        else:
            entrypreset.hide()
            savepreset.hide()
            presetsbox1.show()

            savebutton.set_label("Save Preset")
            self.savestatus = 0
    

    def on_savepreset(self, widget):
        global preset
        global presetmatch
        global entrypreset
        global presetbox1
        global rawpresets

        #preset = presetsbox1.get_child().get_text()
        tree_iter = presetsbox1.get_active_iter()
        preset = entrypreset.get_text()

        presetmatch = ''
        for i in range(len(rawpresets)):
            if rawpresets[i] == preset:
                print('Match!', preset )
                presetmatch = 1

        if tree_iter is not None or preset == '' or presetmatch == 1:
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
            #for i in range(len(rawpresets)):
            #    presetsbox.remove_text(0)

            # Clear text from EntryBox and clear list from ComboBox
            entrypreset.set_text("")
            entrypreset.hide()
            savepreset.hide()
            presetsbox1.show()

            savebutton.set_label("Save Preset")
            self.savestatus = 0


            # Apply settings (which will save new preset as default)
            ApplySettings()

            # Refresh (and therefore, sort) preset list
            GetSettings()

            # Repopulate preset list into ComboBox
            model1 = presetsbox1.get_model()
            presetsbox1.set_model(None)
            model1.clear()
            print(rawpresets)
            boxindex = 0
            for i in range(len(rawpresets)):
                model1.append( [rawpresets[i]] )
                if rawpresets[i] == preset:
                    boxindex = i
            presetsbox1.set_model(model1)
            presetsbox1.set_active(boxindex)


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
            #preset = presetsbox.get_child().get_text()
            tree_iter = presetsbox1.get_active_iter()

            if tree_iter is not None:
                model = presetsbox1.get_model()
                preset = model[tree_iter][0]

            realpreset = preset
            preset = ''
            #presetsbox.get_child().set_text('')
            presetsbox1.set_active(-1)

            # Clear preset list from ComboBox
            #for i in range(len(rawpresets)):
            #    presetsbox1.remove_text(0)
            model1 = presetsbox1.get_model()
            presetsbox1.set_model(None)
            model1.clear()

            # Refresh (and therefore, sort) preset list
            GetSettings()

            # Clear preset (if it is the same as removed preset), or restore preset
            if presetdir1 + '/' + preset + '.preset' == filename:
                preset = ''
            else:
                preset = realpreset

            # Restore preset
            #presetsbox.get_child().set_text(preset)

            # Repopulate preset list into ComboBox
            #for i in range(len(rawpresets)):
            #    presetsbox.append_text(rawpresets[i])
            boxindex = 0
            for i in range(len(rawpresets)):
                model1.append( [rawpresets[i]] )
                if rawpresets[i] == preset:
                    boxindex = i
            presetsbox1.set_model(model1)
            presetsbox1.set_active(boxindex)

            # Apply settings
            ApplySettings()

        dialog.destroy()

    def on_importpreset(self, widget):
        global preset
        global presets
        global rawpresets

        dialog = gtk.FileChooserDialog('Import Preset...',
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

            print('Importing preset:',path_and_name)

            if os.path.isfile(path_and_name[0] + '/' + path_and_name[1]):
                f = open(path_and_name[0] + '/' + path_and_name[1], 'r')
                rawdata = f.read().split('\n')
                f.close

                if rawdata[0] == "mbeq_1197"  and rawdata[1] == "mbeq" and rawdata[2] == "Multiband EQ" :
                    os.system('cp -f "'+path_and_name[0] + '/' + path_and_name[1] + '" ' +presetdir1 )
                    print("Preset imported successfully.")

                    # Refresh (and therefore, sort) preset list
                    GetSettings()

                    # Repopulate preset list into ComboBox
                    model1 = presetsbox1.get_model()
                    presetsbox1.set_model(None)
                    model1.clear()
                    print(rawpresets)
                    boxindex = 0
                    for i in range(len(rawpresets)):
                        model1.append( [rawpresets[i]] )
                        if rawpresets[i] == rawdata[4]:
                            boxindex = i
                    presetsbox1.set_model(model1)
                    presetsbox1.set_active(boxindex)

        dialog.destroy()

    def on_exportpreset(self, widget):
        global preset
        global presets
        dialog = gtk.FileChooserDialog('Export Preset...',
                None, gtk.FILE_CHOOSER_ACTION_SAVE, (gtk.STOCK_CANCEL,
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
            
            print('Export to: ',path_and_name)

            # Verify filename has a .preset extension
            name = path_and_name[1]
            if not '.preset' in path_and_name[1] :
                name = path_and_name[1] + '.preset'
                
            # Save current configration to export as a .preset file
            f = open(path_and_name[0] + '/' + name , 'w')

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

        dialog.destroy()

    def on_aboutdialog(self, widget):
        aboutdialog = AboutDialog()
        aboutdialog.run()

    def destroy_equalizer(self, widget, data=None):
        gtk.main_quit()

    def __init__(self):
        global boxindex

        GetSettings()

        self.savestatus = 0

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

        menu1 = gtk.Menu()

        menu1_item = gtk.MenuItem('Import Preset')
        menu1_item.connect('activate', self.on_importpreset)
        menu1.append(menu1_item)
        menu1_item.show()
        menu1_item = gtk.MenuItem('Export Preset')
        menu1_item.connect('activate', self.on_exportpreset)
        menu1.append(menu1_item)
        menu1_item.show()
        menu1_item =gtk.SeparatorMenuItem()  
        menu1_item.show()
        menu1.append(menu1_item)
        menu1_item = gtk.MenuItem('Exit')
        menu1_item.connect('activate', lambda w: gtk.main_quit())
        menu1.append(menu1_item)
        menu1_item.show()
        root_menu1 = gtk.MenuItem('File')
        root_menu1.show()
        root_menu1.set_submenu(menu1)

        menu2 = gtk.Menu()

        menu2_item = gtk.MenuItem('Reset to defaults')
        menu2_item.connect('activate', self.on_resetsettings)
        menu2.append(menu2_item)
        menu2_item.show()
        menu2_item = gtk.MenuItem('Remove user preset...')
        menu2_item.connect('activate', self.on_removepreset)
        menu2.append(menu2_item)
        menu2_item.show()       
        root_menu2 = gtk.MenuItem('Advanced')
        root_menu2.show()
        root_menu2.set_submenu(menu2)

        menu3 = gtk.Menu()

        menu3_item = gtk.MenuItem('About')
        menu3_item.connect('activate', self.on_aboutdialog)
        menu3.append(menu3_item)
        menu3_item.show()
        root_menu3 = gtk.MenuItem('Help')
        root_menu3.show()
        root_menu3.set_submenu(menu3)

        vbox1 = gtk.VBox(False, 0)
        self.window.add(vbox1)
        vbox1.show()
        menu_bar = gtk.MenuBar()
        vbox1.pack_start(menu_bar, False, False, 0)
        menu_bar.show()
        menu_bar.append(root_menu1)
        menu_bar.append(root_menu2)
        menu_bar.append(root_menu3)

        hbox1 = gtk.HBox(False, 1)
        hbox1.set_border_width(10)
        vbox1.add(hbox1)
        hbox1.show()

        table = gtk.Table(3, 17, False)
        table.set_border_width(3)
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
        preampscale.set_size_request(33, 200)
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
            scale.set_size_request(33, 200)
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
        vbox2.set_border_width(9)
        hbox1.add(vbox2)
        vbox2.show()
        
        presetslabel = gtk.Label()
        presetslabel.set_markup('<small>Preset:</small>')
        vbox2.pack_start(presetslabel, False, False, 0)
        presetslabel.show()

        hbox2 = gtk.HBox(False, 0)
        vbox2.add(hbox2)
        hbox2.show()

        vbox3 = gtk.VBox(True, 1)
        hbox2.add(vbox3)
        vbox3.show()     

        global presetsbox1
        presetmodel = gtk.ListStore(str)
        presetsbox1 = gtk.ComboBox.new_with_model(presetmodel)
        renderer_text = gtk.CellRendererText()
        presetsbox1.pack_start(renderer_text, True)
        presetsbox1.add_attribute(renderer_text, "text", 0)
        presetsbox1.set_property("width-request", 230)
        vbox3.pack_start(presetsbox1, False, False, 0)
        for i in range(len(rawpresets)):
            presetsbox1.append_text(rawpresets[i])

        if boxindex >= 0 :
            presetsbox1.set_active(boxindex)

        presetsbox1.connect('changed', self.on_presetsbox, x)
        
        
        vbox4 = gtk.VBox(True, 1)
        hbox2.add(vbox4)
        vbox4.show()

        global entrypreset
        entrypreset = gtk.Entry()
        entrypreset.set_text("")
        vbox4.pack_start(entrypreset, False, False, 0)

        vbox5 = gtk.VBox(True, 1)
        hbox2.add(vbox5)
        vbox5.show()

        global savepreset
        savepreset = gtk.Button('Save')
        vbox5.pack_start(savepreset, False, False, 0)

        savepreset.connect('clicked', self.on_savepreset)
        
        #entrypreset.show()
        #savepreset.show()
        savepreset.hide()
        entrypreset.hide()
        presetsbox1.show()        

        global savebutton
        savebutton = gtk.Button('Save Preset')
        if boxindex >= 0 :
            savebutton.set_sensitive(False)
        vbox2.pack_start(savebutton, False, False, 0)
        savebutton.connect('clicked', self.on_savebutton)
        savebutton.show()   

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
        quitbutton.set_property("width-request", 230)
        quitbutton.show()

        separator = gtk.HSeparator()
        vbox2.pack_start(separator, False, False, 0)
        separator.set_size_request(130, 10)
        # separator.show()

        self.window.show()


def main():
    gtk.main()
    return 0


if __name__ == '__main__':
    Equalizer()
    main()