import os
import shutil as sh
import numpy as np

def _read_line(filename, line_number):
    s = None
    with open(filename, 'r') as fs:
        for i, line in enumerate(fs.readlines()):
            if i == line_number:
                s = line
    return s

class _GnuplotDeletingFile:
    def __init__(self, filename):
        self.name = filename

    def __del__(self):
        os.remove(self.name)

class _GnuplotScriptTemp(_GnuplotDeletingFile):
    def __init__(self, gnuplot_cmds):
        _GnuplotDeletingFile.__init__(self, '.tmp_gnuplot.gpi')
        with open(self.name, 'w') as fs:
            fs.write(gnuplot_cmds)

class _GnuplotDataTemp(_GnuplotDeletingFile):
    def __init__(self, *args):
        _GnuplotDeletingFile.__init__(self, '.tmp_gnuplot_data.dat')
        data = np.array(args).T
        with open(self.name, 'wb') as fs:
            np.savetxt(fs, data, delimiter=',')

class _GnuplotDataZMatrixTemp(_GnuplotDeletingFile):
    def __init__(self, z_matrix):
        _GnuplotDeletingFile.__init__(self, '.tmp_gnuplot_data_z_matrix.dat')
        with open(self.name, 'wb') as fs:
            np.savetxt(fs, z_matrix, delimiter=',')

def gnuplot(script_name, args_dict={}, data=[], trim_image=True):
    assert script_name is not '.settings'
    tmp_script_name = '.' + script_name
    tmp_settings = '.settings'
    sh.copyfile(script_name, tmp_script_name)

    gnuplot_command = 'gnuplot'

    if data:
        assert 'data' not in args_dict, \
            'Can\'t use \'data\' variable twice.'
        data_temp = _GnuplotDataTemp(*data)
        args_dict['data'] = data_temp.name

    if args_dict:
        gnuplot_command += ' -e "'
        for arg in args_dict.items():
            gnuplot_command += arg[0] + '='
            if isinstance(arg[1], str):
                gnuplot_command += '\'' + arg[1] + '\''
            elif isinstance(arg[1], bool):
                if arg[1] is True:
                    gnuplot_command += '1'
                else:
                    gnuplot_command += '0'
            else:
                gnuplot_command += str(arg[1])
            gnuplot_command += '; '
        gnuplot_command  = gnuplot_command[:-1]
        gnuplot_command += '"'

    gnuplot_command += ' ' + tmp_script_name

    with open(tmp_script_name, 'a') as fs:
        fs.write('\nsave \'%s\'' % tmp_settings)

    os.system(gnuplot_command)

    if trim_image:
        output = _read_line(tmp_settings, 13)
        output = output[14:-2]
        trim_image
        trim_pad_image(output)

    os.remove(tmp_script_name)
    os.remove(tmp_settings)

    return gnuplot_command

def gnuplot_2d(x, y, filename, title='', x_label='', y_label=''):
    gnuplot_cmds = \
    '''
    set datafile separator ","
    set term pngcairo size 30cm,25cm
    set out filename

    unset key
    set border lw 1.5
    set grid lt -1 lc rgb "gray80"

    set title title
    set xlabel x_label
    set ylabel y_label

    plot filename_data u 1:2 w lp pt 6 ps 0.5

    set out
    '''
    scr = _GnuplotScriptTemp(gnuplot_cmds)
    data = _GnuplotDataTemp(x, y)

    args_dict = {
        'filename': filename,
        'filename_data': data.name,
        'title': title,
        'x_label': x_label,
        'y_label': y_label
    }
    gnuplot(scr.name, args_dict)

def gnuplot_3d(x, y, z, filename, title='', x_label='', y_label='', z_label=''):
    gnuplot_cmds = \
    '''
    set datafile separator ","
    set term pngcairo size 30cm,25cm
    set out filename

    unset key
    set border lw 1.5
    set view map

    set title title
    set xlabel x_label
    set ylabel y_label
    set zlabel z_label

    splot filename_data u 1:2:3 w pm3d

    set out
    '''
    scr = _GnuplotScriptTemp(gnuplot_cmds)
    data = _GnuplotDataTemp(x, y, z)

    args_dict = {
        'filename': filename,
        'filename_data': data.name,
        'title': title,
        'x_label': x_label,
        'y_label': y_label,
        'z_label': z_label
    }
    gnuplot(scr.name, args_dict)

def gnuplot_3d_matrix(z_matrix, filename, title='', x_label='', y_label='', z_label=''):
    gnuplot_cmds = \
    '''
    set datafile separator ","
    set term pngcairo size 30cm,25cm
    set out filename

    unset key
    set border lw 1.5
    set view map

    set title title
    set xlabel x_label
    set ylabel y_label
    set zlabel z_label

    splot filename_data matrix w pm3d

    set out
    '''
    scr = _GnuplotScriptTemp(gnuplot_cmds)
    data = _GnuplotDataZMatrixTemp(z_matrix)

    args_dict = {
        'filename': filename,
        'filename_data': data.name,
        'title': title,
        'x_label': x_label,
        'y_label': y_label,
        'z_label': z_label
    }
    gnuplot(scr.name, args_dict)

def trim_pad_image(filename, padding=20):
    os.system('convert %s -trim -bordercolor white -border %i %s' % \
              (filename, padding, filename))
