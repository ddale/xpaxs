'''
This script creates a python interface to a database of fundamental X-ray
fluorescence parameters compiled by W.T. Elam, B.D. Ravel and J.R. Sieber,
published in Radiation Physics and Chemistry, 63 (2), 121 (2002). The
database is published by NIST at
http://www.cstl.nist.gov/acd/839.01/xrfdownload.html

'''
import os
import sys
import zipfile

import h5py
import numpy as np


def create_element(line, elements):
    sym, num, mw, rho = line.split()[1:]
    el = elements.require_group(sym)
    el['atomic_number'] = int(num)
    el['molar_mass'] = float(mw)
    el['molar_mass'].attrs['units'] = 'g/mol'
    el['mass_density'] = float(rho)
    el['mass_density'].attrs['units'] = 'g/cm^3'
    return el

def create_edge(line, edges):
    label, energy, yield_, jump = line.split()[1:]
    edge = edges.require_group(label)
    edge['energy'] = float(energy)
    edge['energy'].attrs['units'] = 'eV'
    edge['fluorescence_yield'] = float(yield_)
    edge['jump_ratio'] = float(jump)
    return edge

def create_lines(elamdb, edge):
    lines = edge.require_group('lines')
    while 1:
        if elamdb[0].startswith('    '):
            iupac, siegbahn, energy, intensity = elamdb.pop(0).split()
            line = lines.require_group(iupac)
            line['IUPAC_symbol'] = iupac
            line['Siegbahn_symbol'] = siegbahn
            line['energy'] = float(energy)
            line['energy'].attrs['units'] = 'eV'
            line['intensity'] = float(intensity)
        else:
            return lines

def create_CK(line, edge):
    ck = edge.require_group('Coster_Kronig')
    temp = line.split()[1:]
    while temp:
        (i,j), temp = temp[:2], temp[2:]
        ck[i] = float(j)
    return ck

def create_CKtotal(line, edge):
    ck_total = edge.require_group('Coster_Kronig_total')
    temp = line.split()[1:]
    while temp:
        (i,j), temp = temp[:2], temp[2:]
        ck_total[i] = float(j)
    return ck_total

def create_photoabsorption(elamdb, element):
    data = []
    while 1:
        line = elamdb[0]

        if line.startswith('    '):
            data.append(np.fromstring(line, sep=' '))
            elamdb.pop(0)
        else:
            data = np.array(data).transpose()
            break

    photo = element.require_group('photoabsorption')
    photo['log_energy'] = data[0]
    photo['log_energy'].attrs['units'] = 'eV'
    photo['log_photoabsorption'] = data[1]
    photo['log_photoabsorption'].attrs['units'] = 'cm^2/g'
    photo['log_photoabsorption_spline'] = data[2]
    return photo

def create_scatter(elamdb, element):
    data = []
    while 1:
        line = elamdb[0]

        if line.startswith('    '):
            data.append(np.fromstring(line, sep=' '))
            elamdb.pop(0)
        else:
            data = np.array(data).transpose()
            break

    scatter = element.require_group('scatter')
    scatter['log_energy'] = data[0]
    scatter['log_energy'].attrs['units'] = 'eV'
    scatter['log_coherent_scatter'] = data[1]
    scatter['log_coherent_scatter'].attrs['units'] = 'cm^2/g'
    scatter['log_coherent_scatter_spline'] = data[2]
    scatter['log_incoherent_scatter'] = data[3]
    scatter['log_incoherent_scatter'].attrs['units'] = 'cm^2/g'
    scatter['log_incoherent_scatter_spline'] = data[4]
    return  scatter

def process_elamdb(data, root):
    '''
    Extracts the data from the zip file and creates an hdf5 archive
    '''
    if os.path.isfile(os.path.join(root, 'elamdb.h5')):
        return

    with open(data) as f:
        elamdb = zipfile.ZipFile(f).read('ElamDB12.txt').split('\r\n')

    with h5py.File(os.path.join(root, 'elamdb.h5'), 'w') as elements:
        while 1:
            line = elamdb.pop(0)
            if line.startswith('/'):
                continue
            elif line.startswith('Element'):
                element = create_element(line, elements)
            elif line.startswith('Edge'):
                edge = create_edge(line, element.require_group('edges'))
            elif line.startswith('  Lines'):
                lines = create_lines(elamdb, edge)
            elif line.startswith('  CK '):
                ck = create_CK(line, edge)
            elif line.startswith('  CKtotal'):
                ck_total = create_CKtotal(line, edge)
            elif line.startswith('Photo'):
                photoabsorption = create_photoabsorption(elamdb, element)
            elif line.startswith('Scatter'):
                scatter = create_scatter(elamdb, element)
            elif line.startswith('EndElement'):
                continue
            elif line.startswith('End'):
                return


if __name__ == '__main__':
    process_elamdb(*sys.argv[1:])
