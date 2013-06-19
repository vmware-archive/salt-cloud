'''
Print out data in a clean and structured way specific to the data being
printed
'''

# Import Salt libs
import salt.utils

UNICODE_TRANS = {
    0xA0: u' ',             # Convert non-breaking space to space
    u'\xe2\x80\x93': u'-',  # Convert en dash to dash
}


def output(data):
    '''
    Print out double layered dict returns (like from list-images and
    list-sizes)
    '''
    ret = []
    colors = salt.utils.get_colors(__opts__.get('color'))
    for top_key in sorted(data):
        ret.append(
            '{0}{1}{2}'.format(colors['GREEN'], top_key, colors['ENDC'])
        )
        for sec_key in sorted(data[top_key]):
            newval = unicode(sec_key).translate(UNICODE_TRANS)
            ret.append('  {0}{1}{2}'.format(
                colors['YELLOW'],
                newval.encode('ascii', 'ignore'),
                colors['ENDC'])
            )
            tval = data[top_key][sec_key]
            for fkey in sorted(tval):
                val = data[top_key][sec_key][fkey]
                if isinstance(val, str) or isinstance(val, int):
                    ret.append('    {0}{1}: {2}{3}'.format(
                        colors['LIGHT_GREEN'],
                        fkey,
                        data[top_key][sec_key][fkey],
                        colors['ENDC'])
                    )
                if isinstance(val, dict):
                    ret.append('    {0}{1}:{2}'.format(
                        colors['LIGHT_GREEN'],
                        fkey,
                        colors['ENDC'])
                    )
                    for ekey in sorted(val):
                        newval = unicode(val[ekey]).translate(UNICODE_TRANS)
                        ret.append('      {0}{1}: {2}{3}'.format(
                            colors['LIGHT_GREEN'],
                            ekey,
                            newval.encode('ascii', 'ignore'),
                            colors['ENDC'])
                        )
    return '\n'.join(ret)
