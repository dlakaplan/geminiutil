import os, yaml
from astropy import units as u
import numpy as np

gmos_data_dir = os.path.join(os.path.dirname(__file__), 'data')
default_gmos_configuration_fname = os.path.join(gmos_data_dir, 'gmos_configuration.yml')

class MissingFITSInformation(ValueError):
    pass


class DetectorGeometry(object):
    """
    Read detector geometry
    """

    def __init__(self, fits_object, gmos_configuration_fname=None):
        if gmos_configuration_fname is None:
            gmos_configuration_fname = default_gmos_configuration_fname
        self.gmos_configuration = yaml.load(file(gmos_configuration_fname))

        if 'dettype' not in fits_object.header:
            raise MissingFITSInformation('"dettype" not present in header - needed for geometry')

        self.detector_type = dict((v, k) for k,v in self.gmos_configuration['detector_type'].iteritems())[fits_object.header['dettype']]

        self.instrument = fits_object.header['instrume'].lower()
        self.generic_pixelscale = u.Quantity.parse_string(
                                        self.gmos_configuration['pixel_scale'][self.instrument][self.detector_type])
        #looping through the chips to get the binning information
        self.y_pixel_scale = []
        self.x_pixel_scale = []
        for i in xrange(3):
            current_ccd = fits_object.fits_data[i+1]
            if 'CCDSUM' not in current_ccd.header:
                raise MissingFITSInformation('"CCDSUM" not present in header of chip %d - needed for geometry' % i)
            x_binning, y_binning = map(int, current_ccd.header['CCDSUM'].split())

            self.x_pixel_scale.append(x_binning * self.generic_pixelscale)
            self.y_pixel_scale.append(y_binning * self.generic_pixelscale)



def display_slices_ds9(slice_table, ds9):
    """
     Function to display the slices on the table
    """

    for lower_edge, upper_edge in zip(slice_table['slice_lower_edge'], slice_table['slice_upper_edge']):
        y_center = 0.5 * (lower_edge + upper_edge) + 1
        height = upper_edge - lower_edge
        x_center = 500
        width = 2000
        ds9.set('regions', 'image; box %d %d %d %d' % (x_center, y_center, width, height))




